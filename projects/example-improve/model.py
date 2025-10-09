# --- model.py ---
import random

from dataclasses import dataclass


# ------------------------------
# Data Structures
# ------------------------------
@dataclass
class Point:
    x: int
    y: int


# ------------------------------
# Snake Class
# ------------------------------
class Snake:
    def __init__(self, initial_position: Point):
        self.body: list[Point] = [initial_position]  # Snake starts with one segment
        self.direction = Point(1, 0)  # Moving right initially
        self.grow_next_move = False  # Flag to handle growth

    @property
    def head(self) -> Point:
        """Return the current head of the snake."""
        return self.body[0]

    def set_direction(self, new_direction: Point):
        """Change direction if not opposite to current."""
        if (
            self.direction.x + new_direction.x != 0
            or self.direction.y + new_direction.y != 0
        ):
            self.direction = new_direction

    def move(self):
        """Move the snake in the current direction."""
        new_head = Point(self.head.x + self.direction.x, self.head.y + self.direction.y)
        self.body.insert(0, new_head)  # Add new head
        if self.grow_next_move:
            self.grow_next_move = False  # Growth applied, reset flag
        else:
            self.body.pop()  # Remove tail if not growing

    def grow(self):
        """Trigger growth on the next move."""
        self.grow_next_move = True


# ------------------------------
# Game Class
# ------------------------------
class Game:
    def __init__(self, size: int = 10):
        self.size = size  # Board size (size x size)
        self.snake = Snake(initial_position=Point(size // 2, size // 2))
        self.food = self.generate_food()
        self.is_running = True

    def generate_food(self):
        """Generate food not overlapping with the snake."""
        while True:
            food_point = Point(
                random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            )
            if food_point not in self.snake.body:
                return food_point

    def update(self):
        """Update the game state: move snake, handle collisions."""
        self.snake.move()

        # Check for food collision
        if self.snake.head == self.food:
            self.snake.grow()
            self.food = self.generate_food()

        # Check for wall collisions
        if not (
            0 <= self.snake.head.x < self.size and 0 <= self.snake.head.y < self.size
        ):
            self.is_running = False

        # Check for self-collision
        if self.snake.head in self.snake.body[1:]:
            self.is_running = False
