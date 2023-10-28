import keyboard


class Controller:
    def __init__(self, game, view):
        self.game = game
        self.view = view

    def handle_input(self):
        if keyboard.is_pressed("up"):
            self.game.move("up")
        elif keyboard.is_pressed("down"):
            self.game.move("down")
        elif keyboard.is_pressed("left"):
            self.game.move("left")
        elif keyboard.is_pressed("right"):
            self.game.move("right")
