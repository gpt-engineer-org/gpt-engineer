import pygame
from snake import Snake
from food import Food

class Game:
    def __init__(self):
        pygame.init()
        self.game_width = 20
        self.game_height = 20
        self.cell_size = 20
        self.screen = pygame.display.set_mode((self.game_width * self.cell_size, self.game_height * self.cell_size))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.snake = Snake([(10, 10)], (1, 0), 3)
        self.food = Food(self.game_width, self.game_height)

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(10)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                    self.snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                    self.snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                    self.snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                    self.snake.change_direction((1, 0))

    def update(self):
        self.snake.move()
        if self.snake.position[0] == self.food.position:
            self.snake.grow()
            self.food.generate()
        if self.snake.check_collision(self.game_width, self.game_height):
            pygame.quit()
            sys.exit()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for segment in self.snake.position:
            pygame.draw.rect(self.screen, (255, 255, 255), (segment[0] * self.cell_size, segment[1] * self.cell_size, self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, (255, 0, 0), (self.food.position[0] * self.cell_size, self.food.position[1] * self.cell_size, self.cell_size, self.cell_size))
