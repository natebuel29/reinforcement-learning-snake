from pygame.locals import *
from random import randint
import pygame
import time
import math
import qLearner
pygame.init()


class Apple:
    def __init__(self,spawn_x,spawn_y):
        self.x = spawn_x
        self.y = spawn_y

        self.loc = (self.x,self.y)
    
    def random_loc(self,snake,apples=[]):
        valid_loc = False

        while not valid_loc:
            apple_x = math.ceil(randint(0, window_width-10)/10.0) * 10
            apple_y = math.ceil(randint(0, window_height-10)/10.0) * 10

            apple_cords = (apple_x, apple_y)

            if apple_cords not in snake and apple_cords not in apples:
                valid_loc = True
        self.x = apple_x
        self.y = apple_y
        self.loc = (self.x,self.y)
    
    def draw(self):
          pygame.draw.rect(surface, RED, pygame.Rect(self.x, self.y, 10, 10))

# MAYBE:create snake class to encapsulate all methods/variables related to snake (move, draw, die, get head, direction)
# and for apple --> (spawn at random location, draw, and cordinates)

window_height = 300
window_width = 300
BLOCK_SIZE = 20
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
xValue = 0
yValue = 0
surface = pygame.display.set_mode((window_width, window_height))
FPS = 20

# display score
def show_score(snake):
    font = pygame.font.Font('freesansbold.ttf', 12)
    text = font.render('Score: '+str(len(snake)-1), True, (255, 255, 255))
    return text

# draw game to surface
def draw_surface(snake, apples):
    surface.fill(BLACK)
    draw_snake(snake)
    for apple in apples:
        apple.draw()
    text = show_score(snake)
    surface.blit(text, (0, 0))
    pygame.display.update()


# def draw_apple(appleX, appleY):
#     # draw a red rect to represent an apple
#     pygame.draw.rect(surface, RED, pygame.Rect(appleX, appleY, 10, 10))


def death(snake):
    head_x = snake[len(snake)-1][0]
    head_y = snake[len(snake)-1][1]
    reason = None
    # if head is outside of screen, then die
    if head_x > window_width - BLOCK_SIZE or head_x < 0 or head_y > window_height - BLOCK_SIZE or head_y < 0:
        reason = 'Border'
        return True, reason

    # if head touches body of snake, then die
    for x_y in snake[0:len(snake)-1]:
        # x_y is tuple of the x and y coordinates
        if x_y == snake[len(snake)-1]:
            reason = 'Self'
            return True, reason

    return False, reason


def game_loop():
    # snake is an array of x & y values grouped in tuples. HEAD IS AT END OF SNAKE
    snake = [(100, 100)]
    running = True
    eaten = False
    # snake begins moving to the right
    xSpeed = 10
    ySpeed = 0

    xValue = snake[len(snake)-1][0] + xSpeed
    yValue = snake[len(snake)-1][1] + ySpeed

    direction = "right"

    starting_x_one = math.ceil(randint(0, window_width-10)/10.0) * 10
    starting_y_one = math.ceil(randint(0, window_height-10)/10.0) * 10

    starting_x_two = math.ceil(randint(0, window_width-10)/10.0) * 10
    starting_y_two = math.ceil(randint(0, window_height-10)/10.0) * 10

    apple_one = Apple(starting_x_one,starting_y_one)
    apple_two = Apple(starting_x_two,starting_y_two)

    apples = [apple_one,apple_two]

    clock = pygame.time.Clock()
    while running == True:
        clock.tick(12)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        #AI only knows about one apple - we must modify state and qLearner file to be functionable with 2 apples
        qLearnerAction = qlearner.act([(xValue, yValue)],direction, apples[0].loc)
        if qLearnerAction == 'left' and direction != "right":
            # move left
            xSpeed = -10
            ySpeed = 0
            direction = "left"
        elif qLearnerAction == 'right' and direction != "left":
            # move right
            xSpeed = 10
            ySpeed = 0
            direction = "right"
        elif qLearnerAction == 'up' and direction != "down":
            # move up
            xSpeed = 0
            ySpeed = -10
            direction = "up"
        elif qLearnerAction == 'down' and direction != "up":
            # move down
            xSpeed = 0
            ySpeed = 10
            direction = "down"
        xValue = snake[len(snake)-1][0] + xSpeed
        yValue = snake[len(snake)-1][1] + ySpeed
        snake.append((xValue, yValue))
        # if head is touching apple, then eat the apple and grow
        for apple in apples:
            if xValue == apple.x and yValue == apple.y:
                eaten = True
                apple.random_loc(snake)

        if eaten == False:
            snake.pop(0)
            
        eaten = False
        running, reason = death(snake)
        running = not running
        draw_surface(snake, apples)

    qlearner.update_qvalues(reason)
    return len(snake)-1, reason


def draw_snake(snake):
    for i in range(0, len(snake)):
        pygame.draw.rect(surface, GREEN, pygame.Rect(
            snake[i][0], snake[i][1], 10, 10))


# Game Loop
game_count = 1
score_count = 0
high_score = 0


qlearner = qLearner.qLearner(window_width, window_height, BLOCK_SIZE)

while True:
    pygame.init()
    qlearner.reset()
    if qlearner.epsilon > 0.04:
        qlearner.epsilon = qlearner.epsilon - 0.01
    else:
        qlearner.epsilon = 0.04
    score, reason = game_loop()
    print(f"Game: {game_count}; Score: {score}; Reason_of_Death: {reason}; Epsilon: {qlearner.epsilon}")
    game_count += 1
    score_count += score

    if score > high_score:
        high_score = score
    if game_count % 100 == 0:
        qlearner.save_qvalues()
        print(f"Highscore: {high_score}; Average Score: {score_count / game_count}")