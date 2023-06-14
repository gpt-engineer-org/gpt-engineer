import pygame
from dataclasses import dataclass

@dataclass
class Snake:
    position: list
    direction: tuple
    length: int

    def move(self):
        self.position.insert(0, (self.position[0][0] + self.direction[0], self.position[0][1] + self.direction[1]))
        self.position.pop()

    def change_direction(self, new_direction):
        self.direction = new_direction

    def grow(self):
        self.length += 1
        self.position.append(self.position[-1])

    def check_collision(self, game_width, game_height):
        if self.position[0] in self.position[1:]:
            return True
        if self.position[0][0] < 0 or self.position[0][0] >= game_width or self.position[0][1] < 0 or self.position[0][1] >= game_height:
            return True
        return False
