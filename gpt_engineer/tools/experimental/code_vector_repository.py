from typing import Dict, List

from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import Document
from llama_index.schema import NodeWithScore
from llama_index.retrievers import BM25Retriever

from gpt_engineer.tools.experimental.document_chunker import DocumentChunker


class CodeVectorRepository:
    def __init__(self):
        self._index = None
        self._query_engine = None
        self._retriever = None

    def _load_documents_from_directory(self, directory_path) -> List[Document]:
        def name_metadata_storer(filename: str) -> Dict:
            return {"filename": filename}

        excluded_file_globs = ["*/.gpteng/*"]

        return SimpleDirectoryReader(
            directory_path,
            recursive=True,
            exclude=excluded_file_globs,
            file_metadata=name_metadata_storer,
        ).load_data()

    def load_from_directory(self, directory_path: str):
        documents = self._load_documents_from_directory(directory_path)

        chunked_langchain_documents = DocumentChunker.chunk_documents(
            [doc.to_langchain_format() for doc in documents]
        )

        chunked_documents = [
            Document.from_langchain_format(doc) for doc in chunked_langchain_documents
        ]

        self._index = VectorStoreIndex.from_documents(chunked_documents)

    def query(self, query_string: str):
        """
        Ask a plain english question about the code base and retrieve a plain english answer
        """

        if self._index is None:
            raise ValueError("Index has not been loaded yet.")

        if self._query_engine is None:
            self._query_engine = self._index.as_query_engine(
                response_mode="tree_summarize"
            )

        return self._query_engine.query(query_string)

    def relevent_code_chunks(
        self, query_string: str, llm: str = "default"
    ) -> List[NodeWithScore]:
        """
        Retrieve code chunks relevent to a prompt
        """

        if self._index is None:
            raise ValueError("Index has not been loaded yet.")

        if self._retriever is None:
            self._retriever = BM25Retriever.from_defaults(self._index, similarity_top_k=2)

        return self._retriever.retrieve(query_string)
