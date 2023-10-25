
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import TextSplitter


import tree_sitter_languages


class CodeSplitter(TextSplitter):
    """Split code using a AST parser.
    """

    def __init__(
        self,
        language: str,
        chunk_lines: int = 40,
        chunk_lines_overlap: int = 15,
        max_chars: int = 1500,
        **kwargs
    ):
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
        """Split incoming code and return chunks using the AST."""

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

        if (
            not tree.root_node.children
            or tree.root_node.children[0].type != "ERROR"
        ):
            chunks = [
                chunk.strip() for chunk in self._chunk_node(tree.root_node, text)
            ]

            return chunks
        else:
            raise ValueError(f"Could not parse code with language {self.language}.")
            

code_splitter = CodeSplitter(
    language="python",
    chunk_lines=40,
    chunk_lines_overlap=15,
    max_chars=1500,
)

character_splitter = CharacterTextSplitter()

# nodes = code_splitter.split_documents(docs)

            
# for doc in docs:
#     print("Page Content:\n", doc.page_content)
#     print("\nMetadata:\n", doc.metadata)
#     print("-------------------------------\n")

def name_metadata_storer(filename: str) -> Dict: 
    return {"filename": filename}

# Load documents and build index
documents = SimpleDirectoryReader('./projects/example-big',recursive=True, file_metadata=name_metadata_storer).load_data()

langchain_docs = [doc.to_langchain_format() for doc in documents]
python_documents = list(filter(lambda x: str(x.metadata["filename"]).endswith('.py'), langchain_docs))
non_python_documents = list(filter(lambda x: not str(x.metadata["filename"]).endswith('.py'), langchain_docs))

split_python_documents_lc = code_splitter.split_documents(python_documents)
split_python_documents = [Document.from_langchain_format(doc) for doc in split_python_documents_lc] 


index = VectorStoreIndex.from_documents(split_python_documents)

query_engine = index.as_query_engine(response_mode="tree_summarize")
response = query_engine.query("What file would i edit to add new default steps to run?")

print(response)

