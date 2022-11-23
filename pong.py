import sys
import math
import random
from time import sleep
import pygame
from pygame.locals import *


class Cfg():
    HEIGHT = 450            # pixels (screen)
    WIDTH = 600             # pixels (screen)
    LINE_LENGTH = 100.0     # pixels (stepping line length)
    PD_WIDTH = 15           # pixels (for paddles and ball)
    PD_HEIGHT = 60          # pixels (for paddles)
    PD_MOVE = 5             # pixels (for paddles)
    PD_BUFFER = 40          # pixels (for paddles)
    FPS = 60                # frames per second


class Const():
    C2PI = 2.0 * math.pi
    CPI2 = math.pi / 2.0
    LEFT = 0
    RIGHT = 1
    WHITE = (255,255,255)
    BLACK = (0,0,0)


class Scoreboard():
    WIDTH = 5               # pixels per block (square)
    COLS = 3                # character columns per digit
    ROWS = 5                # character rows per digit
    OFFSET = 10             # pixels from top of screen

    DIGITS = [
        # 0       1       2       3       4       5       6       7       8       9
        "###" + ".#." + "###" + "###" + "#.#" + "###" + "#.." + "###" + "###" + "###",
        "#.#" + ".#." + "..#" + "..#" + "#.#" + "#.." + "#.." + "..#" + "#.#" + "#.#",
        "#.#" + ".#." + "###" + "###" + "###" + "###" + "###" + "..#" + "###" + "###",
        "#.#" + ".#." + "#.." + "..#" + "..#" + "..#" + "#.#" + "..#" + "#.#" + "..#",
        "###" + ".#." + "###" + "###" + "..#" + "###" + "###" + "..#" + "###" + "..#"
    ]

    def __init__(self, l_score = 0, r_score = 0):
        self.l_score = l_score
        self.r_score = r_score

    def draw(self, surface):
        offset = Scoreboard.WIDTH * (Scoreboard.COLS + 1)
        self._draw_score(surface, self.l_score, (Cfg.WIDTH // 2) - (Cfg.WIDTH // 3), offset)
        self._draw_score(surface, self.r_score, (Cfg.WIDTH // 2) + (Cfg.WIDTH // 3), offset)

    def game_over(self):
        return self.l_score >= 11 or self.r_score >= 11

    def _draw_score(self, surface, score, x, offset):
        if score >= 10:
            self._draw_digit(surface, score // 10, x - offset, Scoreboard.OFFSET)
        self._draw_digit(surface, score % 10, x, Scoreboard.OFFSET)

    def _draw_digit(self, surface, value, x, y):
        for i, row in enumerate(self._get_digit(value)):
            for j, col in enumerate(row):
                if col == "#":
                    pygame.draw.rect(surface, Const.WHITE,
                        (x + j * self.WIDTH, y + i * self.WIDTH, self.WIDTH, self.WIDTH))

    def _get_digit(self, value):
        value *= Scoreboard.COLS
        return [s[value:value + 3] for s in Scoreboard.DIGITS]
 

class Ball(pygame.sprite.Sprite):
    def __init__(self, direction, speed = 3):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.PD_WIDTH, Cfg.PD_WIDTH))
        self.surf.fill(Const.WHITE)

        # Initial position of the ball (center vertically, 2/3 away from directed paddle)
        ypos = (Cfg.HEIGHT // 2) + (Cfg.PD_WIDTH // 2)
        if direction == Const.LEFT:
            xpos = 2 * (Cfg.WIDTH // 3) - (Cfg.PD_WIDTH // 2)
        else:
            xpos = 1 * (Cfg.WIDTH // 3) - (Cfg.PD_WIDTH // 2)
        self.pos = pygame.math.Vector2((xpos, ypos))
        self.speed = speed

        self.rect = self.surf.get_rect()
        self.rect.bottomleft = self.pos

        # Randomly select an angle between -60 and +60 degrees
        angle = (random.random() * math.pi / 1.5) - (math.pi / 3.0)
        if direction == Const.LEFT:
            angle += math.pi
        self.set_angle(angle)

    def move(self):
        self._step_line()
        # Check for collision with top or bottom of screen
        if self.pos.y <= Cfg.PD_WIDTH:
            self.pos.y = Cfg.PD_WIDTH + 1
            self.set_angle(Const.C2PI - self.angle)
        elif self.pos.y >= Cfg.HEIGHT:
            self.pos.y = Cfg.HEIGHT - 1
            self.set_angle(Const.C2PI - self.angle)

    def set_angle(self, angle):
        self.angle = self._normalize_angle(angle)
        # Calculate x and y coordinates of the ball's destination
        x = self.pos.x + (math.cos(self.angle) * Cfg.LINE_LENGTH)
        y = self.pos.y + (math.sin(self.angle) * Cfg.LINE_LENGTH)
        self._prep_line(pygame.math.Vector2((x, y)))

    def _prep_line(self, dst):
        # Bresenham's line algorithm
        # https://wiki2.org/en/Bresenham%27s_line_algorithm
        self.dx = int(round(abs(dst.x - self.pos.x)))
        if dst.x < self.pos.x:
            self.dx = -self.dx

        self.dy = int(round(abs(dst.y - self.pos.y)))
        if dst.y < self.pos.y:
            self.dy = -self.dy

        if abs(self.dy) > abs(self.dx):
            self.yi = -self.speed
            if self.dy < 0:
                self.dy = -self.dy
                self.yi = self.speed
            self.D = (2 * self.dy) - self.dx
        else:
            self.xi = self.speed
            if self.dx < 0:
                self.dx = -self.dx
                self.xi = -self.speed
            self.D = (2 * self.dx) - self.dy

    def _step_line(self):
        if abs(self.dy) > abs(self.dx):
            self._step_line_low()
        else:
            self._step_line_high()
        self.rect.bottomleft = self.pos

    def _step_line_low(self):
        if self.dx > 0:
            self.pos.x += self.speed
        elif self.dx < 0:
            self.pos.x -= self.speed

        if self.D > 0:
            self.pos.y += self.yi
            self.D += 2 * (self.dy - self.dx)
        else:
            self.D += 2 * self.dy

    def _step_line_high(self):
        if self.dy > 0:
            self.pos.y -= self.speed
        elif self.dy < 0:
            self.pos.y += self.speed

        if self.D > 0:
            self.pos.x += self.xi
            self.D += 2 * (self.dx - self.dy)
        else:
            self.D += 2 * self.dx

    def _normalize_angle(self, rads):
        if rads < 0.0:
            rads += Const.C2PI
        elif rads > Const.C2PI:
            rads -= Const.C2PI
        return rads


class Paddle(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.PD_WIDTH, Cfg.PD_HEIGHT))
        self.surf.fill(Const.WHITE)
        self.rect = self.surf.get_rect()
        self.side = side
   
        ypos = (Cfg.HEIGHT // 2) + (Cfg.PD_HEIGHT // 2)
        if side == Const.LEFT:
            self.pos = pygame.math.Vector2((Cfg.PD_BUFFER, ypos))
        else:
            self.pos = pygame.math.Vector2((Cfg.WIDTH - Cfg.PD_BUFFER - Cfg.PD_WIDTH, ypos))
        self.rect.bottomleft = self.pos

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()
            
        if self.side == Const.LEFT:
            if pressed_keys[K_a]:
                self.pos.y -= Cfg.PD_MOVE
            if pressed_keys[K_z]:
                self.pos.y += Cfg.PD_MOVE
        else:
            if pressed_keys[K_k]:
                self.pos.y -= Cfg.PD_MOVE
            if pressed_keys[K_m]:
                self.pos.y += Cfg.PD_MOVE

        # Check for collision with top or bottom of screen
        if self.pos.y < Cfg.PD_HEIGHT:
            self.pos.y = Cfg.PD_HEIGHT
        elif self.pos.y > Cfg.HEIGHT:
            self.pos.y = Cfg.HEIGHT
        self.rect.bottomleft = self.pos


def main():
    pygame.init()
    FramePerSec = pygame.time.Clock()
    pygame.display.set_caption("Pong")
    displaysurface = pygame.display.set_mode((Cfg.WIDTH, Cfg.HEIGHT))

    scoreboard = Scoreboard()
    ball = Ball(Const.RIGHT)
    l_paddle = Paddle(Const.LEFT)
    r_paddle = Paddle(Const.RIGHT)
    paddles = [ l_paddle, r_paddle ]

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
        
        displaysurface.fill(Const.BLACK)
        scoreboard.draw(displaysurface)

        for paddle in paddles:
            displaysurface.blit(paddle.surf, paddle.rect)
        if not scoreboard.game_over():
            displaysurface.blit(ball.surf, ball.rect)
        pygame.display.update()

        if scoreboard.game_over():
            break
        FramePerSec.tick(Cfg.FPS)

        for paddle in paddles:
            paddle.move()
        ball.move()

        # Check for ball collision with paddles
        if ball.rect.colliderect(l_paddle.rect):
            ball.pos.x = l_paddle.rect.x + Cfg.PD_WIDTH + 2
            angle = ball.angle
            if angle > math.pi:
                angle += Const.CPI2
            else:
                angle -= Const.CPI2
            ball.set_angle(angle)
        elif ball.rect.colliderect(r_paddle.rect):
            ball.pos.x = r_paddle.rect.x - Cfg.PD_WIDTH - 2
            angle = ball.angle
            if angle > math.pi:
                angle -= Const.CPI2
            else:
                angle += Const.CPI2
            ball.set_angle(angle)

        # Check for ball exiting left or right, meaning score
        if ball.pos.x >= Cfg.WIDTH - Cfg.PD_WIDTH:
            scoreboard.l_score += 1
            ball = Ball(Const.RIGHT)
        elif ball.pos.x <= 0:
            scoreboard.r_score += 1
            ball = Ball(Const.LEFT)

    # Game over, wait for user to quit
    while True:
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_ESCAPE]:
            break

        quit = False
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
                break
        if quit:
            break

        sleep(0.1)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
