import random

from dataclasses import dataclass


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
