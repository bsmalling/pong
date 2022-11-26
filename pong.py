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
    GAME_SPEED = 4          # ball distance in pixels per frame

    MAX_SCORE = 11          # points required to win

class Const():
    CPI2 = math.pi / 2.0           # 90 degrees
    C2PI = 2.0 * math.pi           # 360 degrees
    MIN_ANGLE = math.pi / 12.0     # 15 degrees

    LEFT = 0
    RIGHT = 1

    COLLIDE_TOP = 0
    COLLIDE_BOTTOM = 1
    COLLIDE_LEFT = 2
    COLLIDE_RIGHT = 3

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
        self._draw_score(surface, self.l_score, (Cfg.WIDTH // 2) - (Cfg.WIDTH // 3))
        self._draw_score(surface, self.r_score, (Cfg.WIDTH // 2) + (Cfg.WIDTH // 3))

    def game_is_over(self):
        return self.l_score >= Cfg.MAX_SCORE or self.r_score >= Cfg.MAX_SCORE

    def _draw_score(self, surface, score, x):
        if score >= 10:
            x_offset = Scoreboard.WIDTH * (Scoreboard.COLS + 1)
            self._draw_digit(surface, score // 10, x - x_offset, Scoreboard.OFFSET)
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
    def __init__(self, direction, speed):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.PD_WIDTH, Cfg.PD_WIDTH))
        self.surf.fill(Const.WHITE)
        self.speed = speed

        # Initial position of the ball (center vertically, 3/4th away from directed paddle)
        self.rect = self.surf.get_rect()
        y = (Cfg.HEIGHT // 2) - (Cfg.PD_WIDTH // 2)
        x = (Cfg.WIDTH // 4) - (Cfg.PD_WIDTH // 2)
        if direction == Const.LEFT:
            x *= 3
        self.rect.topleft = pygame.math.Vector2((x, y))

        # Randomly select an angle between -60 and +60 degrees
        angle = (random.random() * math.pi / 1.5) - (math.pi / 3.0)
        # Make sure angle is not too close to horizontal
        if abs(angle) < Const.MIN_ANGLE:
            if angle < 0:
                angle = 0.0 - Const.MIN_ANGLE
            else:
                angle = Const.MIN_ANGLE
        # Flip direction if ball is going left
        if direction == Const.LEFT:
            angle += math.pi
        self.set_angle(angle)

    def set_angle(self, angle):
        self.angle = self._normalize_angle(angle)
        # Calculate x and y coordinates of the ball's destination
        x = self.rect.left + (math.cos(self.angle) * Cfg.LINE_LENGTH)
        y = self.rect.top  + (math.sin(self.angle) * Cfg.LINE_LENGTH)
        self._prep_line(pygame.math.Vector2((x, y)))

    def set_next_angle(self, collision):
        if collision == Const.COLLIDE_TOP or collision == Const.COLLIDE_BOTTOM:
            self.set_angle(Const.C2PI - self.angle)
        elif collision == Const.COLLIDE_LEFT or collision == Const.COLLIDE_RIGHT:
            self.set_angle(math.pi - self.angle)
        else:
            raise ValueError("Invalid collision type")

    def move(self):
        if abs(self.dy) < abs(self.dx):
            self._step_line_low()
        else:
            self._step_line_high()

    def _prep_line(self, dst):
        # Bresenham's line algorithm
        # https://wiki2.org/en/Bresenham%27s_line_algorithm
        self.dx = int(round(abs(dst.x - self.rect.left)))
        if dst.x < self.rect.left:
            self.dx = -self.dx

        self.dy = int(round(abs(dst.y - self.rect.top)))
        if dst.y < self.rect.top:
            self.dy = -self.dy

        if abs(self.dy) < abs(self.dx):
            self.yi = -self.speed
            if self.dy < 0:
                self.dy = -self.dy
                self.yi = self.speed
            self.diff = (2 * self.dy) - self.dx
        else:
            self.xi = self.speed
            if self.dx < 0:
                self.dx = -self.dx
                self.xi = -self.speed
            self.diff = (2 * self.dx) - self.dy

    def _step_line_low(self):
        if self.dx > 0:
            self.rect.left += self.speed
        elif self.dx < 0:
            self.rect.left -= self.speed

        if self.diff > 0:
            self.rect.top += self.yi
            self.diff += 2 * (self.dy - self.dx)
        else:
            self.diff += 2 * self.dy

    def _step_line_high(self):
        if self.dy > 0:
            self.rect.top -= self.speed
        elif self.dy < 0:
            self.rect.top += self.speed

        if self.diff > 0:
            self.rect.left += self.xi
            self.diff += 2 * (self.dx - self.dy)
        else:
            self.diff += 2 * self.dx

    def _normalize_angle(self, rads):
        # Normalize angle to 0 <= angle < 360 degrees
        if rads < 0.0:
            rads += Const.C2PI
        elif rads >= Const.C2PI:
            rads -= Const.C2PI
        return rads


class Paddle(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.PD_WIDTH, Cfg.PD_HEIGHT))
        self.surf.fill(Const.WHITE)
        self.side = side
   
        # Initial position of the paddle (center vertically)
        self.rect = self.surf.get_rect()
        y = (Cfg.HEIGHT // 2) - (Cfg.PD_HEIGHT // 2)
        x = Cfg.PD_BUFFER
        if side == Const.RIGHT:
            x = Cfg.WIDTH - Cfg.PD_BUFFER - Cfg.PD_WIDTH
        self.rect.topleft = pygame.math.Vector2((x, y))

    def move(self, pressed_keys):
        if self.side == Const.LEFT:
            if pressed_keys[K_a]:
                self.rect.top -= Cfg.PD_MOVE
            if pressed_keys[K_z]:
                self.rect.top += Cfg.PD_MOVE
        else:
            if pressed_keys[K_QUOTE]:
                self.rect.top -= Cfg.PD_MOVE
            if pressed_keys[K_SLASH]:
                self.rect.top += Cfg.PD_MOVE


def main():
    pygame.init()
    fps_timer = pygame.time.Clock()
    pygame.display.set_caption("Pong")
    displaysurface = pygame.display.set_mode((Cfg.WIDTH, Cfg.HEIGHT))

    # Initialize game objects
    speed = Cfg.GAME_SPEED
    scoreboard = Scoreboard()
    ball = Ball(Const.RIGHT, speed)
    l_paddle = Paddle(Const.LEFT)
    r_paddle = Paddle(Const.RIGHT)
    paddles = [ l_paddle, r_paddle ]

    # Main game loop
    while True:
        # Render the game
        displaysurface.fill(Const.BLACK)
        scoreboard.draw(displaysurface)
        for paddle in paddles:
            displaysurface.blit(paddle.surf, paddle.rect)
        if not scoreboard.game_is_over():
            displaysurface.blit(ball.surf, ball.rect)
        pygame.display.update()
        fps_timer.tick(Cfg.FPS)

        # Check for inputs
        if scoreboard.game_is_over():
            break
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()

        # Update the ball
        ball.move()

        # Check for ball collision with top or bottom of screen
        if ball.rect.top < 0:
            ball.rect.top = 0
            ball.set_next_angle(Const.COLLIDE_TOP)
        elif ball.rect.bottom >= Cfg.HEIGHT:
            ball.rect.bottom = Cfg.HEIGHT - 1
            ball.set_next_angle(Const.COLLIDE_BOTTOM)
        # Check for ball collision with paddles
        elif ball.rect.colliderect(l_paddle.rect):
            # Check for collision with top of left addle
            if ball.rect.bottom <= l_paddle.rect.top + ball.speed:
                ball.rect.bottom = l_paddle.rect.top - 1
                ball.set_next_angle(Const.COLLIDE_BOTTOM)
            # Check for collision with bottom of left paddle
            elif ball.rect.top >= l_paddle.rect.bottom - ball.speed:
                ball.rect.top = l_paddle.rect.bottom + 1
                ball.set_next_angle(Const.COLLIDE_TOP)
            else:
                # Collision is in middle of left paddle
                ball.rect.left = l_paddle.rect.right + 1
                ball.set_next_angle(Const.COLLIDE_LEFT)
        elif ball.rect.colliderect(r_paddle.rect):
            # Check for collision with top of right paddle
            if ball.rect.bottom <= r_paddle.rect.top + ball.speed:
                ball.rect.bottom = r_paddle.rect.top - 1
                ball.set_next_angle(Const.COLLIDE_BOTTOM)
            # Check for collision with bottom of right paddle
            elif ball.rect.top >= r_paddle.rect.bottom - ball.speed:
                ball.rect.top = r_paddle.rect.bottom + 1
                ball.set_next_angle(Const.COLLIDE_TOP)
            else:
                # Collision is in middle of right paddle
                ball.rect.right = r_paddle.rect.left - 1
                ball.set_next_angle(Const.COLLIDE_RIGHT)
        # Check for ball exiting left or right, meaning score
        elif ball.rect.left > Cfg.WIDTH:
            scoreboard.l_score += 1
            ball = Ball(Const.RIGHT, speed)
        elif ball.rect.right < 0:
            scoreboard.r_score += 1
            ball = Ball(Const.LEFT, speed)

        # Update the paddles
        for paddle in paddles:
            paddle.move(pressed_keys)
            # Check for paddle collision with top or bottom of screen
            if paddle.rect.top < 0:
                paddle.rect.top = 0
            elif paddle.rect.bottom >= Cfg.HEIGHT:
                paddle.rect.bottom = Cfg.HEIGHT - 1

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
