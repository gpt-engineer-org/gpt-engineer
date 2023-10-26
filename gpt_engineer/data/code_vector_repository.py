from typing import Dict

from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import Document

from document_chunker import DocumentChunker


class CodeVectorRepository:
    def __init__(self):
        self._index = None
        self._query_engine = None

    def load_from_directory(self, directory_path: str):
        def name_metadata_storer(filename: str) -> Dict: 
            return {"filename": filename}

        documents = SimpleDirectoryReader(directory_path,recursive=True, file_metadata=name_metadata_storer).load_data()

        split_langchain_documents = DocumentChunker.chunk_documents([doc.to_langchain_format() for doc in documents])

        split_documents = [Document.from_langchain_format(doc) for doc in split_langchain_documents] 

        self._index = VectorStoreIndex.from_documents(split_documents)
        self._query_engine = self._index.as_query_engine(response_mode="tree_summarize")
    
    def query(self,query_string: str):

        if self._index is None: 
            raise ValueError("Index has not been loaded yet.")
        
        
        if self._query_engine is None: 
            raise ValueError("Query engine has not been loaded yet.")

        return self._query_engine.query(query_string)
