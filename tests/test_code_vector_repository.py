import pytest

from llama_index import Document
from gpt_engineer.data.code_vector_repository import CodeVectorRepository

example_python_file = """
import keyboard
import random
from dataclasses import dataclass


class View:
    def __init__(self, game):
        self.game = game

    def render(self):
        # Print the game state
        for y in range(10):
            for x in range(10):
                if Point(x, y) in self.game.snake:
                    print('S', end='')
                elif Point(x, y) == self.game.food:
                    print('F', end='')
                else:
                    print('.', end='')
            print()
        print()


@dataclass
class Point:
    x: int
    y: int

class Game:
    def __init__(self):
        self.snake = [Point(5, 5)]
        self.food = self.generate_food()
        self.is_running = True

    def generate_food(self):
        return Point(random.randint(0, 10), random.randint(0, 10))

    def update(self):
        # Move the snake
        self.snake.move()

        # Check for collision with food
        if self.snake.head == self.food:
            self.snake.grow()
            self.food = self.generate_food()

        # Check for collision with boundaries
        if not (0 <= self.snake.head.x < 10 and 0 <= self.snake.head.y < 10):
            self.is_running = False

class Controller:
    def __init__(self, game, view):
        self.game = game
        self.view = view

    def handle_input(self):
        if keyboard.is_pressed('up'):
            self.game.move('up')
        elif keyboard.is_pressed('down'):
            self.game.move('down')
        elif keyboard.is_pressed('left'):
            self.game.move('left')
        elif keyboard.is_pressed('right'):
            self.game.move('right')

def main():
    game = Game()
    view = View(game)
    controller = Controller(game, view)

    while game.is_running:
        controller.handle_input()
        game.update()
        view.render()

if __name__ == "__main__":
    main()
"""

def mock_load_documents_from_directory(self, directory_name):
    doc1 = Document()
    doc1.set_content(example_python_file)
    doc1.metadata["filename"] = "src/snake_game.py"

    doc2 = Document()
    doc2.set_content("example non code file which currently isnt loaded into the vector store")
    doc2.metadata["filename"] = "README.md"

    return [doc1, doc2]


@pytest.mark.skip(reason="this test makes queries to an LLM so requires an open ai api key")
def test_load_and_retrieve(monkeypatch):
    # arrange
    monkeypatch.setattr(
        CodeVectorRepository, "_load_documents_from_directory", mock_load_documents_from_directory
    )

    repository = CodeVectorRepository()
    repository.load_from_directory("tmp")

    # act
    document_chunks = repository.relevent_code_chunks("Invert the direction arrows so up moves the snake down, and down moves the snake up.")
    
    # assert
    assert document_chunks.__len__() == 2           #set to return 2 documents 
    assert "Controller" in document_chunks[0].text  #top result should be class to change

@pytest.mark.skip(reason="this test makes queries to an LLM so requires an open ai api key")
def test_load_and_query(monkeypatch):
    # arrange
    monkeypatch.setattr(
        CodeVectorRepository, "_load_documents_from_directory", mock_load_documents_from_directory
    )

    repository = CodeVectorRepository()
    repository.load_from_directory("tmp")

    # act
    response = repository.query("How would I invert the direction arrows so up moves the snake down, and down moves the snake up? ")
    
    # assert
    assert "Controller" in str(response) 
