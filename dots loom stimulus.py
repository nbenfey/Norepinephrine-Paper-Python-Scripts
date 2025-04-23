import time
import random
import pygame
import sys
import math

# Configuration parameters
WINDOW_SIZE = (500, 300)
REPETITIONS = 14
BLANK_SCREEN_TIME = 19
ACTIVE_TIME = 1
NUMBER_OF_DOTS = 25
COLOR_OF_DOTS = (0, 0, 0)
DOT_SIZE = 25
MAX_DOT_SPEED = 3  # Maximum speed of the dots

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

class Dot:
    def __init__(self):
        self.x = random.randint(0, WINDOW_SIZE[0])
        self.y = random.randint(0, WINDOW_SIZE[1])
        angle = random.uniform(0, 2 * math.pi)
        self.move_x = math.cos(angle) * random.uniform(1, MAX_DOT_SPEED)
        self.move_y = math.sin(angle) * random.uniform(1, MAX_DOT_SPEED)

    def update(self):
        self.x += self.move_x
        self.y += self.move_y

        # Reflect the dot if it hits a boundary
        if self.x <= 0 or self.x >= WINDOW_SIZE[0]:
            self.move_x *= -1
        if self.y <= 0 or self.y >= WINDOW_SIZE[1]:
            self.move_y *= -1

    def draw(self):
        pygame.draw.circle(screen, COLOR_OF_DOTS, (int(self.x), int(self.y)), DOT_SIZE // 2)

def draw_dots(dots):
    screen.fill((255, 255, 255))
    for dot in dots:
        dot.update()
        dot.draw()
    pygame.display.flip()

def draw_looming_circle(start_time):
    elapsed_time = time.time() - start_time
    # Increase the rate of growth for the circle
    progress = (elapsed_time / ACTIVE_TIME) * 2
    circle_size = int(min(WINDOW_SIZE) * progress)
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, COLOR_OF_DOTS, (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2), circle_size)
    pygame.display.flip()

input("Press enter to start ... ")

# Main loop
for i in range(REPETITIONS):
    # Blank screen phase
    screen.fill((255, 255, 255))
    pygame.display.flip()
    time.sleep(BLANK_SCREEN_TIME)

    # Active phase for dots
    if i % 2 == 0:
        dots = [Dot() for _ in range(NUMBER_OF_DOTS)]
        start_time = time.time()
        while time.time() - start_time < ACTIVE_TIME:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            draw_dots(dots)
            clock.tick(60)
    # Active phase for the looming circle
    else:
        start_time = time.time()
        while time.time() - start_time < ACTIVE_TIME:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            draw_looming_circle(start_time)
            clock.tick(60)

input("Press enter when you're ready to end")
pygame.quit()
