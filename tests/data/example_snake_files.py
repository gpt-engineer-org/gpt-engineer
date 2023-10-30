python = """
import keyboard
import random
from dataclasses import dataclass


class View:
    def __init__(self, game):
        self.game = game

    def render(self):
        # Print the game state
        for y in range(10):
            for x in range(10):
                if Point(x, y) in self.game.snake:
                    print('S', end='')
                elif Point(x, y) == self.game.food:
                    print('F', end='')
                else:
                    print('.', end='')
            print()
        print()


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

class Controller:
    def __init__(self, game, view):
        self.game = game
        self.view = view

    def handle_input(self):
        if keyboard.is_pressed('up'):
            self.game.move('up')
        elif keyboard.is_pressed('down'):
            self.game.move('down')
        elif keyboard.is_pressed('left'):
            self.game.move('left')
        elif keyboard.is_pressed('right'):
            self.game.move('right')

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
"""


html = """
<!DOCTYPE html>
<html>
<head>
    <title>Snake Game</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
    <h1>Snake Game</h1>
    <canvas id="gameCanvas" width="400" height="400"></canvas>
    <h2 id="score">Score: 0</h2>
    <script src="script.js"></script>
</body>
</html>
"""

css = """
body {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #000;
    color: #fff;
    font-family: Arial, sans-serif;
}

#gameCanvas {
    border: 1px solid #fff;
}

h1, h2 {
    text-align: center;
}

"""

javascript = """
var canvas = document.getElementById('gameCanvas');
var context = canvas.getContext('2d');

var box = 20;
var score = 0;
var food = null;

var snake = [];
snake[0] = { x: 10 * box, y: 10 * box };

document.addEventListener('keydown', direction);
var d;

function direction(event) {
    if (event.keyCode == 37 && d != "RIGHT") {
        d = "LEFT";
    } else if (event.keyCode == 38 && d != "DOWN") {
        d = "UP";
    } else if (event.keyCode == 39 && d != "LEFT") {
        d = "RIGHT";
    } else if (event.keyCode == 40 && d != "UP") {
        d = "DOWN";
    }
}

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < snake.length; i++) {
        context.fillStyle = (i == 0) ? "green" : "white";
        context.fillRect(snake[i].x, snake[i].y, box, box);
    }

    if (food == null) {
        food = {
            x: Math.floor(Math.random() * 19 + 1) * box,
            y: Math.floor(Math.random() * 19 + 1) * box
        }
    }

    context.fillStyle = "red";
    context.fillRect(food.x, food.y, box, box);

    var snakeX = snake[0].x;
    var snakeY = snake[0].y;

    if (d == "LEFT") snakeX -= box;
    if (d == "UP") snakeY -= box;
    if (d == "RIGHT") snakeX += box;
    if (d == "DOWN") snakeY += box;

    if (snakeX == food.x && snakeY == food.y) {
        score++;
        food = null;
    } else {
        snake.pop();
    }

    var newHead = {
        x: snakeX,
        y: snakeY
    }

    if (snakeX < 0 || snakeY < 0 || snakeX > 19 * box || snakeY > 19 * box || collision(newHead, snake)) {
        clearInterval(game);
    }

    snake.unshift(newHead);

    document.getElementById('score').innerHTML = "Score: " + score;
}

function collision(head, array) {
    for (var i = 0; i < array.length; i++) {
        if (head.x == array[i].x && head.y == array[i].y) {
            return true;
        }
    }
    return false;
}

var game = setInterval(draw, 100);
"""

java = """
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import javax.swing.ImageIcon;
import javax.swing.JPanel;
import javax.swing.Timer;

public class SnakeGame extends JPanel implements ActionListener {

    private final int B_WIDTH = 300;
    private final int B_HEIGHT = 300;
    private final int DOT_SIZE = 10;
    private final int ALL_DOTS = 900;
    private final int RAND_POS = 29;
    private final int DELAY = 140;

    private final int x[] = new int[ALL_DOTS];
    private final int y[] = new int[ALL_DOTS];

    private int dots;
    private int apple_x;
    private int apple_y;

    private boolean leftDirection = false;
    private boolean rightDirection = true;
    private boolean upDirection = false;
    private boolean downDirection = false;
    private boolean inGame = true;

    private Timer timer;
    private Image ball;
    private Image apple;
    private Image head;

    public SnakeGame() {

        initBoard();
    }

    private void initBoard() {

        addKeyListener(new TAdapter());
        setBackground(Color.black);
        setFocusable(true);

        setPreferredSize(new Dimension(B_WIDTH, B_HEIGHT));
        loadImages();
        initGame();
    }

    private void loadImages() {

        ImageIcon iid = new ImageIcon("src/resources/dot.png");
        ball = iid.getImage();

        ImageIcon iia = new ImageIcon("src/resources/apple.png");
        apple = iia.getImage();

        ImageIcon iih = new ImageIcon("src/resources/head.png");
        head = iih.getImage();
    }

    private void initGame() {

        dots = 3;

        for (int z = 0; z < dots; z++) {
            x[z] = 50 - z * 10;
            y[z] = 50;
        }

        locateApple();

        timer = new Timer(DELAY, this);
        timer.start();
    }

    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);

        doDrawing(g);
    }

    private void doDrawing(Graphics g) {

        if (inGame) {

            g.drawImage(apple, apple_x, apple_y, this);

            for (int z = 0; z < dots; z++) {
                if (z == 0) {
                    g.drawImage(head, x[z], y[z], this);
                } else {
                    g.drawImage(ball, x[z], y[z], this);
                }
            }

            Toolkit.getDefaultToolkit().sync();

        } else {

            gameOver(g);
        }
    }

    private void gameOver(Graphics g) {

        String msg = "Game Over";
        Font small = new Font("Helvetica", Font.BOLD, 14);
        FontMetrics metr = getFontMetrics(small);

        g.setColor(Color.white);
        g.setFont(small);
        g.drawString(msg, (B_WIDTH - metr.stringWidth(msg)) / 2, B_HEIGHT / 2);
    }

    private void checkApple() {

        if ((x[0] == apple_x) && (y[0] == apple_y)) {

            dots++;
            locateApple();
        }
    }

    private void move() {

        for (int z = dots; z > 0; z--) {
            x[z] = x[(z - 1)];
            y[z] = y[(z - 1)];
        }

        if (leftDirection) {
            x[0] -= DOT_SIZE;
        }

        if (rightDirection) {
            x[0] += DOT_SIZE;
        }

        if (upDirection) {
            y[0] -= DOT_SIZE;
        }

        if (downDirection) {
            y[0] += DOT_SIZE;
        }
    }

    private void checkCollision() {

        for (int z = dots; z > 0; z--) {

            if ((z > 4) && (x[0] == x[z]) && (y[0] == y[z])) {
                inGame = false;
            }
        }

        if (y[0] >= B_HEIGHT) {
            inGame = false;
        }

        if (y[0] < 0) {
            inGame = false;
        }

        if (x[0] >= B_WIDTH) {
            inGame = false;
        }

        if (x[0] < 0) {
            inGame = false;
        }

        if (!inGame) {
            timer.stop();
        }
    }

    private void locateApple() {

        int r = (int) (Math.random() * RAND_POS);
        apple_x = ((r * DOT_SIZE));

        r = (int) (Math.random() * RAND_POS);
        apple_y = ((r * DOT_SIZE));
    }

    @Override
    public void actionPerformed(ActionEvent e) {

        if (inGame) {

            checkApple();
            checkCollision();
            move();
        }

        repaint();
    }

    private class TAdapter extends KeyAdapter {

        @Override
        public void keyPressed(KeyEvent e) {

            int key = e.getKeyCode();

            if ((key == KeyEvent.VK_LEFT) && (!rightDirection)) {
                leftDirection = true;
                upDirection = false;
                downDirection = false;
            }

            if ((key == KeyEvent.VK_RIGHT) && (!leftDirection)) {
                rightDirection = true;
                upDirection = false;
                downDirection = false;
            }

            if ((key == KeyEvent.VK_UP) && (!downDirection)) {
                upDirection = true;
                rightDirection = false;
                leftDirection = false;
            }

            if ((key == KeyEvent.VK_DOWN) && (!upDirection)) {
                downDirection = true;
                rightDirection = false;
                leftDirection = false;
            }
        }
    }
}
"""

c_sharp = """
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace SnakeGame
{
    // Model
    public class Game
    {
        public Snake Snake { get; set; }
        public Point Food { get; set; }
        public int Score { get; set; }
        public bool Over { get; set; }

        public Game()
        {
            Snake = new Snake();
            Food = new Point();
            Score = 0;
            Over = false;
        }
    }

    public class Snake
    {
        public Queue<Point> Body { get; set; }
        public Direction Direction { get; set; }

        public Snake()
        {
            Body = new Queue<Point>();
            Direction = Direction.Right;
        }
    }

    public class Point
    {
        public int X { get; set; }
        public int Y { get; set; }
    }

    public enum Direction
    {
        Up,
        Down,
        Left,
        Right
    }

    // View
    public class GameView
    {
        public void Draw(Game game)
        {
            Console.Clear();
            foreach (var point in game.Snake.Body)
            {
                Console.SetCursorPosition(point.X, point.Y);
                Console.Write("O");
            }
            Console.SetCursorPosition(game.Food.X, game.Food.Y);
            Console.Write("F");
            Console.SetCursorPosition(0, 0);
            Console.Write("Score: " + game.Score);
        }
    }

    // Controller
    public class GameController
    {
        private Game game;
        private GameView view;

        public GameController(Game game, GameView view)
        {
            this.game = game;
            this.view = view;
        }

        public void Start()
        {
            while (!game.Over)
            {
                Thread.Sleep(100);
                MoveSnake();
                CheckCollision();
                view.Draw(game);
            }
        }

        private void MoveSnake()
        {
            var head = game.Snake.Body.Last();
            var newHead = new Point { X = head.X, Y = head.Y };
            switch (game.Snake.Direction)
            {
                case Direction.Up:
                    newHead.Y--;
                    break;
                case Direction.Down:
                    newHead.Y++;
                    break;
                case Direction.Left:
                    newHead.X--;
                    break;
                case Direction.Right:
                    newHead.X++;
                    break;
            }
            game.Snake.Body.Enqueue(newHead);
            if (newHead.X == game.Food.X && newHead.Y == game.Food.Y)
            {
                game.Score++;
                game.Food = new Point { X = new Random().Next(1, 10), Y = new Random().Next(1, 10) };
            }
            else
            {
                game.Snake.Body.Dequeue();
            }
        }

        private void CheckCollision()
        {
            var head = game.Snake.Body.Last();
            if (head.X < 0 || head.Y < 0 || head.X >= 10 || head.Y >= 10)
            {
                game.Over = true;
            }
            if (game.Snake.Body.Take(game.Snake.Body.Count - 1).Any(p => p.X == head.X && p.Y == head.Y))
            {
                game.Over = true;
            }
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            var game = new Game();
            var view = new GameView();
            var controller = new GameController(game, view);
            controller.Start();
        }
    }
}
"""

html = """
"""
