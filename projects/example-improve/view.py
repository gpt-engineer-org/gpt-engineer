from model import Point

class View:
    def __init__(self, game):
        self.game = game

    def render(self):
        # Print the game state (10x10 board)
        for y in range(self.game.size):
            for x in range(self.game.size):
                current = Point(x, y)
                if current == self.game.snake.head:
                    print("H", end="")  # Head of the snake
                elif current in self.game.snake.body[1:]:
                    print("S", end="")  # Body of the snake
                elif current == self.game.food:
                    print("F", end="")  # Food
                else:
                    print(".", end="")  # Empty space
            print()
        print()
