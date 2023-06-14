import pygame
import random

class Food:
    def __init__(self, game_width, game_height):
        self.position = (0, 0)
        self.game_width = game_width
        self.game_height = game_height
        self.generate()

    def generate(self):
        self.position = (random.randint(0, self.game_width - 1), random.randint(0, self.game_height - 1))
