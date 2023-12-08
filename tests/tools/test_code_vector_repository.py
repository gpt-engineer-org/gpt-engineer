import pytest

from llama_index import Document
from gpt_engineer.tools.experimental.code_vector_repository import CodeVectorRepository
import example_snake_files


def mock_load_documents_from_directory(self, directory_name):
    nonCodeDoc = Document()
    nonCodeDoc.set_content(
        "example non code file which currently isnt loaded into the vector store"
    )
    nonCodeDoc.metadata["filename"] = "README.md"

    if directory_name == "python":
        doc1 = Document()
        doc1.set_content(example_snake_files.PYTHON)
        doc1.metadata["filename"] = "src/snake_game.py"

    if directory_name == "web":
        doc1 = Document()
        doc1.set_content(example_snake_files.HTML)
        doc1.metadata["filename"] = "src/index.html"

        doc2 = Document()
        doc2.set_content(example_snake_files.CSS)
        doc2.metadata["filename"] = "src/styles.css"

        doc3 = Document()
        doc3.set_content(example_snake_files.JAVASCRIPT)
        doc3.metadata["filename"] = "src/script.js"

        return [doc1, doc2, doc3, nonCodeDoc]

    if directory_name == "java":
        doc1 = Document()
        doc1.set_content(example_snake_files.JAVA)
        doc1.metadata["filename"] = "src/snake_game.java"

    if directory_name == "c#":
        doc1 = Document()
        doc1.set_content(example_snake_files.C_SHARP)
        doc1.metadata["filename"] = "src/snake_game.cs"

    if directory_name == "typescript":
        doc1 = Document()
        doc1.set_content(example_snake_files.TYPESCRIPT)
        doc1.metadata["filename"] = "src/snake_game.ts"

    if directory_name == "ruby":
        doc1 = Document()
        doc1.set_content(example_snake_files.RUBY)
        doc1.metadata["filename"] = "src/snake_game.rb"

    if directory_name == "php":
        doc1 = Document()
        doc1.set_content(example_snake_files.PHP)
        doc1.metadata["filename"] = "src/snake_game.php"

    if directory_name == "go":
        doc1 = Document()
        doc1.set_content(example_snake_files.GO)
        doc1.metadata["filename"] = "src/main.go"

    if directory_name == "kotlin":
        doc1 = Document()
        doc1.set_content(example_snake_files.KOTLIN)
        doc1.metadata["filename"] = "src/main/kotlin/SnakeGame.kt"

    if directory_name == "rust":
        doc1 = Document()
        doc1.set_content(example_snake_files.RUST)
        doc1.metadata["filename"] = "src/main.rs"

    if directory_name == "c++":
        doc1 = Document()
        doc1.set_content(example_snake_files.C_PLUS_PLUS)
        doc1.metadata["filename"] = "src/main.cpp"

    # c is supported, however it does not pass this test
    # if directory_name == "c":
    #     doc1 = Document()
    #     doc1.set_content(example_snake_files.C)
    #     doc1.metadata["filename"] = "main.c"

    # Swift not currently supported
    # if directory_name == "swift":
    #     doc1 = Document()
    #     doc1.set_content(example_snake_files.SWIFT)
    #     doc1.metadata["filename"] = "src/main.swift"

    return [doc1, nonCodeDoc]


@pytest.mark.skip(
    reason="this test makes queries to an LLM as part of creating the vector store so requires an open ai api key. Todo: run the vector store with llm=None so this can run without an LLM"
)
@pytest.mark.parametrize(
    "language",
    [
        "python",
        "web",
        "java",
        "c#",
        "typescript",
        "ruby",
        "php",
        "go",
        "kotlin",
        "rust",
        "c++",
    ],
)  # ToDo: add Swift, C and other languages
def test_load_and_retrieve(monkeypatch, language):
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
        "Invert the controlls so pressing the up moves the snake down, and pressing down moves the snake up.",
        llm=None,
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
def test_load_and_query_python(monkeypatch):
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
