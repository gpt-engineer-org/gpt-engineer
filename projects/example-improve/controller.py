import keyboard


class Controller:
    def __init__(self, game, view):
        self.game = game
        self.view = view

    def handle_input(self):
        if keyboard.is_pressed("up") and not hasattr(self, "last_key_pressed"):
            self.game.move("down")
            self.last_key_pressed = "up"
        elif hasattr(self, "last_key_pressed") and self.last_key_pressed == "up":
            self.game.move("right")
            del self.last_key_pressed
        elif keyboard.is_pressed("down"):
            self.game.move("up")
        elif keyboard.is_pressed("left"):
            self.game.move("right")
        elif keyboard.is_pressed("right"):
            self.game.move("left")
