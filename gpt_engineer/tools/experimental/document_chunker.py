"""
Provides tools for splitting documents into chunks based on programming language.

Classes
-------
CodeSplitter
    Splits code into chunks using an AST parser for a specified programming language.
SortedDocuments
    A named tuple to hold sorted documents by language and other types.
DocumentChunker
    Chunks documents based on their programming language and provides a list of chunked documents.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

import tree_sitter_languages

from langchain.docstore.document import Document
from langchain.text_splitter import TextSplitter

from gpt_engineer.tools.experimental.supported_languages import SUPPORTED_LANGUAGES


class CodeSplitter(TextSplitter):
    """
    Splits code into chunks using an AST parser.

    This class extends TextSplitter and provides functionality to split code into manageable
    chunks using an AST parser for a specified programming language.

    Attributes:
        language (str): The programming language of the code.
        chunk_lines (int): The number of lines per chunk.
        chunk_lines_overlap (int): The number of overlapping lines between chunks.
        max_chars (int): The maximum number of characters per chunk.
    """

    def __init__(
        self,
        language: str,
        chunk_lines: int = 40,
        chunk_lines_overlap: int = 15,
        max_chars: int = 1500,
        **kwargs,
    ):
        """
        Initializes a new instance of the CodeSplitter class.

        Parameters:
            language (str): The programming language of the code.
            chunk_lines (int): The number of lines per chunk.
            chunk_lines_overlap (int): The number of overlapping lines between chunks.
            max_chars (int): The maximum number of characters per chunk.
        """
        super().__init__(**kwargs)

        self.language = language
        self.chunk_lines = chunk_lines
        self.chunk_lines_overlap = chunk_lines_overlap
        self.max_chars = max_chars

    def _chunk_node(self, node: Any, text: str, last_end: int = 0) -> List[str]:
        new_chunks = []
        current_chunk = ""
        for child in node.children:
            if child.end_byte - child.start_byte > self.max_chars:
                # Child is too big, recursively chunk the child
                if len(current_chunk) > 0:
                    new_chunks.append(current_chunk)
                current_chunk = ""
                new_chunks.extend(self._chunk_node(child, text, last_end))
            elif (
                len(current_chunk) + child.end_byte - child.start_byte > self.max_chars
            ):
                # Child would make the current chunk too big, so start a new chunk
                new_chunks.append(current_chunk)
                current_chunk = text[last_end : child.end_byte]
            else:
                current_chunk += text[last_end : child.end_byte]
            last_end = child.end_byte
        if len(current_chunk) > 0:
            new_chunks.append(current_chunk)
        return new_chunks

    def split_text(self, text: str) -> List[str]:
        """
        Split incoming code and return chunks using the AST.

        Parameters
        ----------
        text : str
            The code text to be split into chunks.

        Returns
        -------
        List[str]
            A list of code chunks split according to the AST of the language.

        Raises
        ------
        ValueError
            If the code cannot be parsed with the language's parser.
        """

        try:
            parser = tree_sitter_languages.get_parser(self.language)
        except Exception as e:
            print(
                f"Could not get parser for language {self.language}. Check "
                "https://github.com/grantjenks/py-tree-sitter-languages#license "
                "for a list of valid languages."
            )
            raise e

        tree = parser.parse(bytes(text, "utf-8"))

        if not tree.root_node.children or tree.root_node.children[0].type != "ERROR":
            chunks = [chunk.strip() for chunk in self._chunk_node(tree.root_node, text)]

            return chunks
        else:
            raise ValueError(f"Could not parse code with language {self.language}.")


class SortedDocuments(NamedTuple):
    by_language: Dict[str, List[Document]]
    other: List[Document]


class DocumentChunker:
    """
    Chunks documents based on their programming language.

    Methods
    -------
    chunk_documents(documents: List[Document]) -> List[Document]
        Chunks the given documents based on their programming language and returns the chunked documents.
    """

    @staticmethod
    def chunk_documents(documents: List[Document]) -> List[Document]:
        """
        Chunks the given documents based on their programming language.

        Parameters
        ----------
        documents : List[Document]
            A list of Document objects to be chunked.

        Returns
        -------
        List[Document]
            A list of Document objects that have been chunked.
        """

        chunked_documents = []

        sorted_documents = _sort_documents_by_programming_language_or_other(documents)

        for language, language_documents in sorted_documents.by_language.items():
            code_splitter = CodeSplitter(
                language=language.lower(),
                chunk_lines=40,
                chunk_lines_overlap=15,
                max_chars=1500,
            )

            chunked_documents.extend(code_splitter.split_documents(language_documents))

        # for now only include code files!
        # chunked_documents.extend(sorted_documents.other)

        return chunked_documents


@staticmethod
def _sort_documents_by_programming_language_or_other(
    documents: List[Document],
) -> SortedDocuments:
    docs_to_split = defaultdict(list)
    other_docs = []

    for doc in documents:
        filename = str(doc.metadata.get("filename"))
        extension = Path(filename).suffix
        language_found = False

        for lang in SUPPORTED_LANGUAGES:
            if extension in lang["extensions"]:
                doc.metadata["is_code"] = True
                doc.metadata["code_language"] = lang["name"]
                doc.metadata["code_language_tree_sitter_name"] = lang[
                    "tree_sitter_name"
                ]
                docs_to_split[lang["tree_sitter_name"]].append(doc)
                language_found = True
                break

        if not language_found:
            doc.metadata["isCode"] = False
            other_docs.append(doc)

    return SortedDocuments(by_language=dict(docs_to_split), other=other_docs)
