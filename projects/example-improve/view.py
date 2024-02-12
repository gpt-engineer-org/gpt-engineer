from model import Point


class View:
    def __init__(self, game):
        self.game = game

    def render(self):
        # Print the game state
        for y in range(10):
            for x in range(10):
                if Point(x, y) in self.game.snake:
                    print("S", end="")
                elif Point(x, y) == self.game.food:
                    print("F", end="")
                else:
                    print(".", end="")
            print()
        print()
