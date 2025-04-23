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
DOT_SPEED = 3  # Constant speed for all dots

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

class Dot:
    def __init__(self, coherent=False, common_angle=None):
        self.x = random.randint(0, WINDOW_SIZE[0])
        self.y = random.randint(0, WINDOW_SIZE[1])
        if coherent and common_angle is not None:
            angle = common_angle
        else:
            angle = random.uniform(0, 2 * math.pi)
        self.move_x = math.cos(angle) * DOT_SPEED
        self.move_y = math.sin(angle) * DOT_SPEED
        self.coherent = coherent

    def update(self):
        if self.coherent:
            # Allow coherent dots to move off-screen
            self.x += self.move_x
            self.y += self.move_y
        else:
            # Random motion dots still reflect at the boundary
            self.x += self.move_x
            self.y += self.move_y

            if self.x <= 0 or self.x >= WINDOW_SIZE[0]:
                self.move_x *= -1
            if self.y <= 0 or self.y >= WINDOW_SIZE[1]:
                self.move_y *= -1

    def draw(self):
        # Only draw the dot if it's within the window
        if 0 <= self.x <= WINDOW_SIZE[0] and 0 <= self.y <= WINDOW_SIZE[1]:
            pygame.draw.circle(screen, COLOR_OF_DOTS, (int(self.x), int(self.y)), DOT_SIZE // 2)

def draw_dots(dots):
    screen.fill((255, 255, 255))
    for dot in dots:
        dot.update()
        dot.draw()
    pygame.display.flip()

input("Press enter to start ... ")

# Main loop
for i in range(REPETITIONS):
    # Blank screen phase
    screen.fill((255, 255, 255))
    pygame.display.flip()
    time.sleep(BLANK_SCREEN_TIME)

    # Active phase
    coherent = i % 2 != 0
    if coherent:  # Coherent motion phase
        common_angle = random.uniform(0, 2 * math.pi)
        dots = [Dot(coherent=True, common_angle=common_angle) for _ in range(NUMBER_OF_DOTS)]
    else:  # Random motion phase
        dots = [Dot() for _ in range(NUMBER_OF_DOTS)]

    # Display dots
    start_time = time.time()
    while time.time() - start_time < ACTIVE_TIME:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        draw_dots(dots)
        clock.tick(60)

input("Press enter when you're ready to end")
pygame.quit()
