PYTHON = """
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


HTML = """
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

CSS = """
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

JAVASCRIPT = """
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

JAVA = """
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

C_SHARP = """
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

TYPESCRIPT = """
// Importing necessary modules
import { Application, Graphics, Keyboard } from 'pixi.js';

// Defining the Model class
class Model {
    // The snake's body is represented as an array of points
    body: Array<{x: number, y: number}>;

    constructor() {
        this.body = [{x: 0, y: 0}];
    }

    // Method to move the snake
    move(direction: {x: number, y: number}) {
        // Add a new head in the direction of movement
        this.body.unshift({
            x: this.body[0].x + direction.x,
            y: this.body[0].y + direction.y
        });

        // Remove the tail
        this.body.pop();
    }
}

// Defining the View class
class View {
    // The view needs a reference to the model and the PIXI application
    model: Model;
    app: Application;
    graphics: Graphics;

    constructor(model: Model, app: Application) {
        this.model = model;
        this.app = app;
        this.graphics = new Graphics();
        this.app.stage.addChild(this.graphics);
    }

    // Method to render the snake
    render() {
        // Clear the previous frame
        this.graphics.clear();

        // Draw each part of the snake's body
        for (let part of this.model.body) {
            this.graphics.beginFill(0xFFFFFF);
            this.graphics.drawRect(part.x * 10, part.y * 10, 10, 10);
            this.graphics.endFill();
        }
    }
}

// Defining the Controller class
class Controller {
    // The controller needs a reference to the model and the view
    model: Model;
    view: View;
    direction: {x: number, y: number};

    constructor(model: Model, view: View) {
        this.model = model;
        this.view = view;
        this.direction = {x: 1, y: 0};

        // Set up keyboard controls
        window.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    // Method to handle keyboard input
    handleKeydown(event: KeyboardEvent) {
        switch (event.key) {
            case 'ArrowUp':
                this.direction = {x: 0, y: -1};
                break;
            case 'ArrowDown':
                this.direction = {x: 0, y: 1};
                break;
            case 'ArrowLeft':
                this.direction = {x: -1, y: 0};
                break;
            case 'ArrowRight':
                this.direction = {x: 1, y: 0};
                break;
        }
    }

    // Method to update the game state
    update() {
        this.model.move(this.direction);
        this.view.render();
    }
}

// Create the PIXI application
let app = new Application({width: 800, height: 600});

// Create the MVC components
let model = new Model();
let view = new View(model, app);
let controller = new Controller(model, view);

// Start the game loop
setInterval(() => controller.update(), 100);
"""

RUBY = """
require 'io/console'

# Model
class Game
  attr_accessor :score, :snake, :food

  def initialize
    @score = 0
    @snake = [[2, 2]]
    @food = [6, 4]
  end

  def move(direction)
    head = @snake.first.dup
    case direction
    when 'up'
      head[0] -= 1
    when 'down'
      head[0] += 1
    when 'left'
      head[1] -= 1
    when 'right'
      head[1] += 1
    end
    @snake.unshift(head)

    if @snake.first == @food
      @score += 1
      @food = [rand(1..8), rand(1..8)]
    else
      @snake.pop
    end
  end

  def game_over?
    head = @snake.first
    @snake[1..-1].include?(head) || head[0] == 0 || head[1] == 0 || head[0] == 9 || head[1] == 9
  end
end

# View
class View
  def render(game)
    system('clear')
    puts "Score: #{game.score}"
    (0..9).each do |i|
      (0..9).each do |j|
        if game.snake.include?([i, j])
          print 'S'
        elsif game.food == [i, j]
          print 'F'
        else
          print '.'
        end
      end
      puts
    end
  end
end

# Controller
class Controller
  def initialize
    @game = Game.new
    @view = View.new
    @direction = 'right'
  end

  def play
    loop do
      @view.render(@game)
      break if @game.game_over?

      input = IO.console.getch
      case input
      when 'w'
        @direction = 'up'
      when 's'
        @direction = 'down'
      when 'a'
        @direction = 'left'
      when 'd'
        @direction = 'right'
      end
      @game.move(@direction)
    end
    puts "Game Over! Your score was #{@game.score}."
  end
end

Controller.new.play

"""

PHP = """
<?php
// Model
class Snake {
    public $body;
    public $direction;

    public function __construct() {
        $this->body = array(array(2, 0), array(1, 0), array(0, 0));
        $this->direction = 'right';
    }

    public function move() {
        $head = current($this->body);
        switch($this->direction) {
            case 'right':
                $this->body[] = array($head[0] + 1, $head[1]);
                break;
            case 'left':
                $this->body[] = array($head[0] - 1, $head[1]);
                break;
            case 'up':
                $this->body[] = array($head[0], $head[1] - 1);
                break;
            case 'down':
                $this->body[] = array($head[0], $head[1] + 1);
                break;
        }
        array_shift($this->body);
    }

    public function changeDirection($new_direction) {
        $this->direction = $new_direction;
    }
}

// View
class GameView {
    public function render($snake) {
        $output = '';
        for ($y=0; $y<20; $y++) {
            for ($x=0; $x<20; $x++) {
                if (in_array(array($x, $y), $snake->body)) {
                    $output .= 'X';
                } else {
                    $output .= ' ';
                }
            }
            $output .= "\n";
        }
        echo $output;
    }
}

// Controller
class GameController {
    public $snake;
    public $view;

    public function __construct() {
        $this->snake = new Snake();
        $this->view = new GameView();
    }

    public function start() {
        while (true) {
            $this->view->render($this->snake);
            $this->snake->move();
            sleep(1);
        }
    }

    public function changeDirection($new_direction) {
        $this->snake->changeDirection($new_direction);
    }
}

// Game loop
$game = new GameController();
$game->start();
?>
"""

SWIFT = """
import Foundation
import Cocoa

// MARK: - Model
struct Point {
    var x: Int
    var y: Int
}

class Snake {
    var body: [Point]
    var direction: Direction

    init(startPoint: Point) {
        body = [startPoint]
        direction = .right
    }

    func move() {
        let head = body.first!
        var newHead = head

        switch direction {
        case .up:
            newHead.y += 1
        case .down:
            newHead.y -= 1
        case .left:
            newHead.x -= 1
        case .right:
            newHead.x += 1
        }

        body.insert(newHead, at: 0)
        body.removeLast()
    }

    func grow() {
        let tail = body.last!
        body.append(tail)
    }
}

enum Direction {
    case up
    case down
    case left
    case right
}

// MARK: - View
class GameView {
    func draw(snake: Snake) {
        for point in snake.body {
            print("O", terminator: "")
        }
        print("\n")
    }
}

// MARK: - Controller
class GameController {
    var snake: Snake
    var view: GameView

    init() {
        snake = Snake(startPoint: Point(x: 0, y: 0))
        view = GameView()
    }

    func start() {
        while true {
            snake.move()
            view.draw(snake: snake)
            sleep(1)
        }
    }

    func handleKey(key: String) {
        switch key {
        case "w":
            snake.direction = .up
        case "s":
            snake.direction = .down
        case "a":
            snake.direction = .left
        case "d":
            snake.direction = .right
        default:
            break
        }
    }
}

// MARK: - Main
let gameController = GameController()
gameController.start()
"""

GO = """
package main

import (
	"fmt"
	"os"
	"os/exec"
	"time"
	"math/rand"
	"bufio"
	"syscall"
	"unsafe"
)

// Model
type Point struct {
	X int
	Y int
}

type Snake struct {
	Body []Point
	Dir  string
}

type Game struct {
	Snake       Snake
	Food        Point
	Score       int
	Width       int
	Height      int
}

// View
func (game *Game) Render() {
	clearScreen()
	for y := 0; y < game.Height; y++ {
		for x := 0; x < game.Width; x++ {
			point := Point{X: x, Y: y}
			switch {
			case point == game.Food:
				fmt.Print("F")
			case game.Snake.Contains(point):
				fmt.Print("S")
			default:
				fmt.Print(" ")
			}
		}
		fmt.Println()
	}
	fmt.Println("Score:", game.Score)
}

// Controller
func (game *Game) Update() {
	head := game.Snake.Body[0]
	switch game.Snake.Dir {
	case "up":
		head.Y--
	case "down":
		head.Y++
	case "left":
		head.X--
	case "right":
		head.X++
	}

	if head.X < 0 || head.Y < 0 || head.X >= game.Width || head.Y >= game.Height {
		game.Score = -1
		return
	}

	if game.Snake.Contains(head) {
		game.Score = -1
		return
	}

	if head == game.Food {
		game.Score++
		game.Food = Point{rand.Intn(game.Width), rand.Intn(game.Height)}
	} else {
		game.Snake.Body = game.Snake.Body[:len(game.Snake.Body)-1]
	}

	game.Snake.Body = append([]Point{head}, game.Snake.Body...)
}

func (snake *Snake) Contains(point Point) bool {
	for _, bodyPoint := range snake.Body {
		if bodyPoint == point {
			return true
		}
	}
	return false
}

func clearScreen() {
	cmd := exec.Command("clear")
	cmd.Stdout = os.Stdout
	cmd.Run()
}

func main() {
	game := &Game{
		Snake: Snake{
			Body: []Point{{10, 10}},
			Dir:  "right",
		},
		Food:   Point{15, 15},
		Score:  0,
		Width:  20,
		Height: 20,
	}

	go func() {
		reader := bufio.NewReader(os.Stdin)
		for {
			char, _, err := reader.ReadRune()
			if err != nil {
				panic(err)
			}

			switch char {
			case 'w':
				game.Snake.Dir = "up"
			case 's':
				game.Snake.Dir = "down"
			case 'a':
				game.Snake.Dir = "left"
			case 'd':
				game.Snake.Dir = "right"
			}
		}
	}()

	for game.Score >= 0 {
		game.Render()
		time.Sleep(time.Second / 5)
		game.Update()
	}
}
"""

KOTLIN = """
import java.awt.Color
import java.awt.Dimension
import java.awt.Font
import java.awt.FontMetrics
import java.awt.Graphics
import java.awt.Image
import java.awt.Toolkit
import java.awt.event.ActionEvent
import java.awt.event.ActionListener
import java.awt.event.KeyAdapter
import java.awt.event.KeyEvent
import javax.swing.ImageIcon
import javax.swing.JPanel
import javax.swing.Timer

class Board : JPanel(), ActionListener {

    private val B_WIDTH = 300
    private val B_HEIGHT = 300
    private val DOT_SIZE = 10
    private val ALL_DOTS = 900
    private val RAND_POS = 29
    private val DELAY = 140

    private val x = IntArray(ALL_DOTS)
    private val y = IntArray(ALL_DOTS)

    private var dots: Int = 0
    private var apple_x: Int = 0
    private var apple_y: Int = 0

    private var leftDirection = false
    private var rightDirection = true
    private var upDirection = false
    private var downDirection = false
    private var inGame = true

    private lateinit var timer: Timer
    private lateinit var apple: Image
    private lateinit var dot: Image
    private lateinit var head: Image

    init {
        initBoard()
    }

    private fun initBoard() {

        addKeyListener(TAdapter())
        background = Color.black
        isFocusable = true

        preferredSize = Dimension(B_WIDTH, B_HEIGHT)
        loadImages()
        initGame()
    }

    private fun loadImages() {

        val iid = ImageIcon("src/resources/apple.png")
        apple = iid.image

        val iid2 = ImageIcon("src/resources/dot.png")
        dot = iid2.image

        val iid3 = ImageIcon("src/resources/head.png")
        head = iid3.image
    }

    private fun initGame() {

        dots = 3

        for (z in 0 until dots) {
            x[z] = 50 - z * 10
            y[z] = 50
        }

        locateApple()

        timer = Timer(DELAY, this)
        timer.start()
    }

    override fun paintComponent(g: Graphics) {
        super.paintComponent(g)

        doDrawing(g)
    }

    private fun doDrawing(g: Graphics) {

        if (inGame) {

            g.drawImage(apple, apple_x, apple_y, this)

            for (z in 0 until dots) {
                if (z == 0) {
                    g.drawImage(head, x[z], y[z], this)
                } else {
                    g.drawImage(dot, x[z], y[z], this)
                }
            }

            Toolkit.getDefaultToolkit().sync()

        } else {

            gameOver(g)
        }
    }

    private fun gameOver(g: Graphics) {

        val msg = "Game Over"
        val font = Font("Helvetica", Font.BOLD, 14)
        val metrics: FontMetrics = this.getFontMetrics(font)

        g.color = Color.white
        g.font = font
        g.drawString(msg, (B_WIDTH - metrics.stringWidth(msg)) / 2, B_HEIGHT / 2)
    }

    private fun checkApple() {

        if (x[0] == apple_x && y[0] == apple_y) {

            dots++
            locateApple()
        }
    }

    private fun move() {

        for (z in dots downTo 1) {
            x[z] = x[z - 1]
            y[z] = y[z - 1]
        }

        if (leftDirection) {
            x[0] -= DOT_SIZE
        }

        if (rightDirection) {
            x[0] += DOT_SIZE
        }

        if (upDirection) {
            y[0] -= DOT_SIZE
        }

        if (downDirection) {
            y[0] += DOT_SIZE
        }
    }

    private fun checkCollision() {

        for (z in dots downTo 1) {
            if (z > 4 && x[0] == x[z] && y[0] == y[z]) {
                inGame = false
            }
        }

        if (y[0] >= B_HEIGHT) {
            inGame = false
        }

        if (y[0] < 0) {
            inGame = false
        }

        if (x[0] >= B_WIDTH) {
            inGame = false
        }

        if (x[0] < 0) {
            inGame = false
        }

        if (!inGame) {
            timer.stop()
        }
    }

    private fun locateApple() {

        val r = (Math.random() * RAND_POS).toInt()
        apple_x = r * DOT_SIZE

        r = (Math.random() * RAND_POS).toInt()
        apple_y = r * DOT_SIZE
    }

    override fun actionPerformed(e: ActionEvent) {

        if (inGame) {

            checkApple()
            checkCollision()
            move()
        }

        repaint()
    }

    private inner class TAdapter : KeyAdapter() {

        override fun keyPressed(e: KeyEvent) {

            val key = e.keyCode

            if (key == KeyEvent.VK_LEFT && !rightDirection) {
                leftDirection = true
                upDirection = false
                downDirection = false
            }

            if (key == KeyEvent.VK_RIGHT && !leftDirection) {
                rightDirection = true
                upDirection = false
                downDirection = false
            }

            if (key == KeyEvent.VK_UP && !downDirection) {
                upDirection = true
                rightDirection = false
                leftDirection = false
            }

            if (key == KeyEvent.VK_DOWN && !upDirection) {
                downDirection = true
                rightDirection = false
                leftDirection = false
            }
        }
    }
}
"""
RUST = """
extern crate termion;

use std::io;
use std::io::stdout;
use std::io::Write;
use std::thread;
use std::time::Duration;
use termion::raw::IntoRawMode;
use termion::input::TermRead;
use termion::event::Key;

// Define the size of the game board
const BOARD_SIZE: usize = 10;

// Define the game state
struct GameState {
    snake: Snake,
    food: Food,
}

// Define the snake
struct Snake {
    body: Vec<(usize, usize)>,
    direction: Direction,
}

// Define the food
struct Food {
    position: (usize, usize),
}

// Define the possible directions the snake can move
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

// Implement the game state
impl GameState {
    fn new() -> GameState {
        GameState {
            snake: Snake::new(),
            food: Food::new(),
        }
    }

    // Update the game state
    fn update(&mut self) {
        self.snake.move();
        if self.snake.eats(&self.food) {
            self.food = Food::new();
        }
    }
}

// Implement the snake
impl Snake {
    fn new() -> Snake {
        Snake {
            body: vec![(BOARD_SIZE / 2, BOARD_SIZE / 2)],
            direction: Direction::Right,
        }
    }

    // Move the snake in the current direction
    fn move(&mut self) {
        let (head_x, head_y) = self.body[0];
        match self.direction {
            Direction::Up => self.body.insert(0, (head_x, head_y - 1)),
            Direction::Down => self.body.insert(0, (head_x, head_y + 1)),
            Direction::Left => self.body.insert(0, (head_x - 1, head_y)),
            Direction::Right => self.body.insert(0, (head_x + 1, head_y)),
        }
        self.body.pop();
    }

    // Check if the snake eats the food
    fn eats(&self, food: &Food) -> bool {
        self.body[0] == food.position
    }
}

// Implement the food
impl Food {
    fn new() -> Food {
        Food {
            position: (rand::random::<usize>() % BOARD_SIZE, rand::random::<usize>() % BOARD_SIZE),
        }
    }
}

// Implement the view
fn render(game_state: &GameState) {
    for y in 0..BOARD_SIZE {
        for x in 0..BOARD_SIZE {
            if game_state.snake.body.contains(&(x, y)) {
                print!("S");
            } else if game_state.food.position == (x, y) {
                print!("F");
            } else {
                print!(" ");
            }
        }
        println!();
    }
}

// Implement the controller
fn controller(game_state: &mut GameState) {
    let stdin = io::stdin();
    for c in stdin.keys() {
        match c.unwrap() {
            Key::Char('q') => break,
            Key::Up => game_state.snake.direction = Direction::Up,
            Key::Down => game_state.snake.direction = Direction::Down,
            Key::Left => game_state.snake.direction = Direction::Left,
            Key::Right => game_state.snake.direction = Direction::Right,
            _ => {}
        }
    }
}

fn main() {
    let mut game_state = GameState::new();
    let mut stdout = stdout().into_raw_mode().unwrap();

    loop {
        write!(stdout, "{}", termion::clear::All).unwrap();
        render(&game_state);
        stdout.flush().unwrap();
        game_state.update();
        thread::sleep(Duration::from_millis(1000));
    }
}
"""

C_PLUS_PLUS = """
#include <iostream>
#include <conio.h>
#include <windows.h>
using namespace std;

bool gameOver;
const int width = 20;
const int height = 20;
int x, y, fruitX, fruitY, score;
int tailX[100], tailY[100];
int nTail;
enum eDirecton { STOP = 0, LEFT, RIGHT, UP, DOWN};
eDirecton dir;

void Setup()
{
    gameOver = false;
    dir = STOP;
    x = width / 2;
    y = height / 2;
    fruitX = rand() % width;
    fruitY = rand() % height;
    score = 0;
}
void Draw()
{
    system("cls");
    for (int i = 0; i < width+2; i++)
        cout << "#";
    cout << endl;

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            if (j == 0)
                cout << "#";
            if (i == y && j == x)
                cout << "*";
            else if (i == fruitY && j == fruitX)
                cout << "%";
            else
            {

                bool print = false;
                for (int k = 0; k < nTail ; k++)
                {
                    if (tailX[k] == j && tailY[k] == i)
                    {
                        cout << "*"; print = true;
                    }
                }
                if (!print)
                    cout << " ";

            }

            if (j == width - 1)
                cout << "#";
        }
        cout << endl;
    }

    for (int i = 0; i < width+2; i++)
        cout << "#";
    cout << endl;
    cout << "Score:" << score << endl;

}

void Input()
{
    if (_kbhit())
    {
        switch (_getch())
        {
        case 'a':
            dir = LEFT;
            break;
        case 'd':
            dir = RIGHT;
            break;
        case 'w':
            dir = UP;
            break;
        case 's':
            dir = DOWN;
            break;
        case 'x':
            gameOver = true;
            break;
        }
    }
}

void algorithm()
{
    int prevX = tailX[0];
    int prevY = tailY[0];
    int prev2X, prev2Y;
    tailX[0] = x;
    tailY[0] = y;

    for(int i = 1; i < nTail ; i++)
    {
        prev2X = tailX[i];
        prev2Y = tailY[i];
        tailX[i] = prevX;
        tailY[i] = prevY;
        prevX = prev2X;
        prevY = prev2Y;
    }

    switch (dir)
    {
    case LEFT:
        x--;
        break;
    case RIGHT:
        x++;
        break;
    case UP:
        y--;
        break;
    case DOWN:
        y++;
        break;
    default:
        break;
    }
    if (x >= width)
        x = 0; else if (x < 0) x = width - 1;
    if (y >= height)
        y = 0; else if (y < 0) y = height - 1;

    for (int i = 0; i < nTail ; i++)
        if (tailX[i] == x && tailY[i] == y)
            gameOver = true;

    if (x == fruitX && y == fruitY)
    {
        score += 10;
        fruitX = rand() % width;
        fruitY = rand() % height;
        nTail++;
    }
}

int main()
{
    Setup();
    while (!gameOver)
    {
        Draw();
        Input();
        algorithm();
    }
    return 0;
}
"""

C = """
#include <stdio.h>
#include <conio.h>
#include <windows.h>
#include <stdlib.h>

#define WIDTH 20
#define HEIGHT 20
#define MAX_SNAKE_SIZE WIDTH *HEIGHT

// Model
typedef struct {
    int x, y;
} Point;

typedef struct {
    Point body[MAX_SNAKE_SIZE];
    int size;
    Point direction;
} Snake;

typedef struct {
    Point position;
    int isEaten;
} Fruit;

// View
void gotoxy(int x, int y) {
    COORD coord;
    coord.X = x;
    coord.Y = y;
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
}

void drawBoard() {
    int i;
    for (i = 0; i < WIDTH + 2; i++) {
        gotoxy(i, 0);
        printf("#");
        gotoxy(i, HEIGHT + 1);
        printf("#");
    }
    for (i = 0; i < HEIGHT + 2; i++) {
        gotoxy(0, i);
        printf("#");
        gotoxy(WIDTH + 1, i);
        printf("#");
    }
}

void drawSnake(Snake* snake) {
    int i;
    for (i = 0; i < snake->size; i++) {
        gotoxy(snake->body[i].x, snake->body[i].y);
        printf("*");
    }
}

void drawFruit(Fruit* fruit) {
    gotoxy(fruit->position.x, fruit->position.y);
    printf("@");
}

// Controller
void initGame(Snake* snake, Fruit* fruit) {
    snake->size = 1;
    snake->body[0].x = WIDTH / 2;
    snake->body[0].y = HEIGHT / 2;
    snake->direction.x = 0;
    snake->direction.y = 1;

    fruit->position.x = rand() % WIDTH;
    fruit->position.y = rand() % HEIGHT;
    fruit->isEaten = 0;
}

void updateSnake(Snake* snake) {
    memmove(&snake->body[1], &snake->body[0], sizeof(Point) * (snake->size - 1));
    snake->body[0].x += snake->direction.x;
    snake->body[0].y += snake->direction.y;
}

void updateFruit(Snake* snake, Fruit* fruit) {
    if (snake->body[0].x == fruit->position.x && snake->body[0].y == fruit->position.y) {
        fruit->isEaten = 1;
        snake->size++;
    }
    if (fruit->isEaten) {
        fruit->position.x = rand() % WIDTH;
        fruit->position.y = rand() % HEIGHT;
        fruit->isEaten = 0;
    }
}

void updateDirection(Snake* snake, char key) {
    switch (key) {
    case 'w':
        snake->direction.x = 0;
        snake->direction.y = -1;
        break;
    case 's':
        snake->direction.x = 0;
        snake->direction.y = 1;
        break;
    case 'a':
        snake->direction.x = -1;
        snake->direction.y = 0;
        break;
    case 'd':
        snake->direction.x = 1;
        snake->direction.y = 0;
        break;
    }
}

int isGameOver(Snake* snake) {
    if (snake->body[0].x <= 0 || snake->body[0].x >= WIDTH || snake->body[0].y <= 0 || snake->body[0].y >= HEIGHT)
        return 1;
    int i;
    for (i = 1; i < snake->size; i++) {
        if (snake->body[0].x == snake->body[i].x && snake->body[0].y == snake->body[i].y)
            return 1;
    }
    return 0;
}

int main() {
    Snake snake;
    Fruit fruit;
    char key;

    initGame(&snake, &fruit);

    while (1) {
        drawBoard();
        drawSnake(&snake);
        drawFruit(&fruit);

        if (_kbhit()) {
            key = _getch();
            updateDirection(&snake, key);
        }

        updateSnake(&snake);
        updateFruit(&snake, &fruit);

        if (isGameOver(&snake)) {
            break;
        }

        Sleep(100);
        system("cls");
    }

    printf("Game Over!\n");

    return 0;
}
"""
