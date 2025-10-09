# --- controller.py ---
import keyboard

from model import Point  # Import Point to define directions


class Controller:
    def __init__(self, game, view):
        self.game = game
        self.view = view

    def handle_input(self):
        # We need a reference to the snake to change its direction
        snake = self.game.snake

        # Check for key presses and set the snake's direction using Point objects.
        # Note: We must call set_direction on the snake object.

        # UP: Change Y by -1
        if keyboard.is_pressed("up"):
            snake.set_direction(Point(0, -1))

        # DOWN: Change Y by +1
        elif keyboard.is_pressed("down"):
            snake.set_direction(Point(0, 1))

        # LEFT: Change X by -1
        elif keyboard.is_pressed("left"):
            snake.set_direction(Point(-1, 0))

        # RIGHT: Change X by +1
        elif keyboard.is_pressed("right"):
            snake.set_direction(Point(1, 0))

        # Optional: Add an exit key
        elif keyboard.is_pressed("esc"):
            self.game.is_running = False
