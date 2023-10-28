from controller import Controller
from model import Game
from view import View


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
