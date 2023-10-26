from typing import Any, List
from pathlib import Path
from collections import defaultdict
from langchain.text_splitter import TextSplitter
from langchain.docstore.document import Document
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
        
class CodeSplitterFactory:
    def __init__(self):
        self._splitters = {}
    
    _extension_to_language = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.ts': 'TypeScript',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.go': 'Go',
        '.rs': 'Rust',
        '.kt': 'Kotlin'
    }
        
    def get_splitter(self, extension: str) -> CodeSplitter:
        if extension not in self._splitters:
            language = self._extension_to_language.get(extension)
            if language:
                self._splitters[extension] = CodeSplitter(
                    language=language.lower(),
                    chunk_lines=40,
                    chunk_lines_overlap=15,
                    max_chars=1500,
                )
            else:
                self._splitters[extension] = None
        return self._splitters[extension]     

class DocumentChunker: 
    def chunk_documents(documents: List[Document]) -> List[Document]:
        code_splitter_factory = CodeSplitterFactory()
        split_documents = []

        docs_to_split = defaultdict(list)
        other_docs = []
        
        for doc in documents:           
            filename = str(doc.metadata.get("filename"))
            extension = Path(filename).suffix
            
            if extension in code_splitter_factory._extension_to_language:
                doc.metadata["isCode"] = True
                doc.metadata["language"]= code_splitter_factory._extension_to_language[extension]
                docs_to_split[extension].append(doc)
            else:
                other_docs.append(doc)

        for extension, docs in docs_to_split.items():
            code_splitter = code_splitter_factory.get_splitter(extension)
            if code_splitter:
                split_documents.extend(code_splitter.split_documents(docs))
        
        
        split_documents.extend(other_docs)

        return split_documents
