import pytest

from llama_index import Document
from gpt_engineer.data.code_vector_repository import CodeVectorRepository
import example_snake_files


def mock_load_documents_from_directory(self, directory_name):
    nonCodeDoc = Document()
    nonCodeDoc.set_content(
        "example non code file which currently isnt loaded into the vector store"
    )
    nonCodeDoc.metadata["filename"] = "README.md"

    if directory_name == "python":
        doc1 = Document()
        doc1.set_content(example_snake_files.python)
        doc1.metadata["filename"] = "src/snake_game.py"

    if directory_name == "web":
        doc1 = Document()
        doc1.set_content(example_snake_files.html)
        doc1.metadata["filename"] = "src/index.html"

        doc2 = Document()
        doc2.set_content(example_snake_files.css)
        doc2.metadata["filename"] = "src/styles.css"

        doc3 = Document()
        doc3.set_content(example_snake_files.javascript)
        doc3.metadata["filename"] = "src/script.js"

        return [doc1, doc2, doc3, nonCodeDoc]

    if directory_name == "java":
        doc1 = Document()
        doc1.set_content(example_snake_files.java)
        doc1.metadata["filename"] = "src/snake_game.java"

    if directory_name == "c_sharp":
        doc1 = Document()
        doc1.set_content(example_snake_files.c_sharp)
        doc1.metadata["filename"] = "src/snake_game.cs"

    return [doc1, nonCodeDoc]


@pytest.mark.skip(
    reason="this test makes queries to an LLM so requires an open ai api key"
)
@pytest.mark.parametrize("language", [("python"), ("web"), ("java"), ("c_sharp")])
def test_load_and_retrieve_python(monkeypatch, language):
    # arrange
    monkeypatch.setattr(
        CodeVectorRepository,
        "_load_documents_from_directory",
        mock_load_documents_from_directory,
    )

    repository = CodeVectorRepository()
    repository.load_from_directory(language)

    # act
    document_chunks = repository.relevent_code_chunks(
        "Invert the controlls so pressing the up moves the snake down, and pressing down moves the snake up."
    )

    # assert
    assert document_chunks.__len__() == 2  # set to return 2 documents
    assert (
        "up" in document_chunks[0].text.lower()
    )  # code should include section that sets directions
    assert "down" in document_chunks[0].text.lower()


@pytest.mark.skip(
    reason="this test makes queries to an LLM so requires an open ai api key"
)
def test_load_and_query(monkeypatch):
    # arrange
    monkeypatch.setattr(
        CodeVectorRepository,
        "_load_documents_from_directory",
        mock_load_documents_from_directory,
    )

    repository = CodeVectorRepository()
    repository.load_from_directory("python")

    # act
    response = repository.query(
        "How would I invert the direction arrows so up moves the snake down, and down moves the snake up? "
    )

    # assert
    assert "Controller" in str(response)
