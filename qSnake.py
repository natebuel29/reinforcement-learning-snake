from pygame.locals import *
from random import randint
import pygame
import time
import math
import qLearner
pygame.init()


# MAYBE:create snake class to encapsulate all methods/variables related to snake (move, draw, die, get head, direction)
# and for apple --> (spawn at random location, draw, and cordinates)

window_height = 360
window_width = 360
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
def draw_surface(snake, appleX, appleY):
    surface.fill(BLACK)
    draw_snake(snake)
    draw_apple(appleX, appleY)
    text = show_score(snake)
    surface.blit(text, (0, 0))
    pygame.display.update()


def draw_apple(appleX, appleY):
    # draw a red rect to represent an apple
    pygame.draw.rect(surface, RED, pygame.Rect(appleX, appleY, 10, 10))


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

    appleX = math.ceil(randint(0, window_width-10)/10.0) * 10
    appleY = math.ceil(randint(0, window_height-10)/10.0) * 10
    clock = pygame.time.Clock()
    while running == True:
        clock.tick(12)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        qLearnerAction = qlearner.act([(xValue, yValue)], (appleX, appleY))
        if qLearnerAction == 'left':
            # move left
            xSpeed = -10
            ySpeed = 0
        elif qLearnerAction == 'right':
            # move right
            xSpeed = 10
            ySpeed = 0
        elif qLearnerAction == 'up':
            # move up
            xSpeed = 0
            ySpeed = -10
        elif qLearnerAction == 'down':
            # move down
            xSpeed = 0
            ySpeed = 10
        xValue = snake[len(snake)-1][0] + xSpeed
        yValue = snake[len(snake)-1][1] + ySpeed
        snake.append((xValue, yValue))
        # if head is touching apple, then eat the apple and grow
        if xValue == appleX and yValue == appleY:
            eaten = True
            apple_cords = get_new_apple_cord(snake)
            appleX = apple_cords[0]
            appleY = apple_cords[1]

        if eaten == False:
            snake.pop(0)
        eaten = False
        running, reason = death(snake)
        running = not running
        draw_surface(snake, appleX, appleY)

    qlearner.update_qvalues(reason)
    return len(snake)-1, reason


def get_new_apple_cord(snake):
    not_in_snake = False

    while not not_in_snake:
        appleX = math.ceil(randint(0, window_width-10)/10.0) * 10
        appleY = math.ceil(randint(0, window_height-10)/10.0) * 10

        apple_cords = (appleX, appleY)

        if apple_cords not in snake:
            not_in_snake = True
    return apple_cords


def draw_snake(snake):
    for i in range(0, len(snake)):
        pygame.draw.rect(surface, GREEN, pygame.Rect(
            snake[i][0], snake[i][1], 10, 10))


# Game Loop
game_count = 1

qlearner = qLearner.qLearner(window_width, window_height, BLOCK_SIZE)

while True:
    pygame.init()
    qlearner.reset()
    if game_count > 100:
        qlearner.epsilon = 0
    else:
        qlearner.epsilon = .1
    score, reason = game_loop()
    print(f"Game: {game_count}; Score: {score}; Reason_of_Death: {reason}")
    game_count += 1
    if game_count % 100 == 0:
        qlearner.save_qvalues()
