import sys
import math
import random
import pygame
from pygame.locals import *


class Cfg():
    HEIGHT = 450            # pixels (screen)
    WIDTH = 600             # pixels (screen)
    SP_WIDTH = 15           # pixels (for ball and paddles)
    SP_HEIGHT = 60          # pixels (for paddles)
    PD_MOVE = 5             # pixels (for paddles)
    SIDE_BUFFER = 40        # pixels (for paddles)
    FPS = 60                # frames per second


class Const():
    LEFT = 0
    RIGHT = 1
    WHITE = (255,255,255)
    BLACK = (0,0,0)


class Scoreboard():
    WIDTH = 5               # pixels per block (square)
    DWIDTH = 3              # character columns per digit
    DHEIGHT = 5             # character rows per digit
    YOFFSET = 10            # pixels from top of screen
    DIGITS = [
        "###"+".#."+"###"+"###"+"#.#"+"###"+"#.."+"###"+"###"+"###",
        "#.#"+".#."+"..#"+"..#"+"#.#"+"#.."+"#.."+"..#"+"#.#"+"#.#",
        "#.#"+".#."+"###"+"###"+"###"+"###"+"###"+"..#"+"###"+"###",
        "#.#"+".#."+"#.."+"..#"+"..#"+"..#"+"#.#"+"..#"+"#.#"+"..#",
        "###"+".#."+"###"+"###"+"..#"+"###"+"###"+"..#"+"###"+"..#"
    ]

    def __init__(self, l_score = 0, r_score = 0):
        self.l_score = l_score
        self.r_score = r_score

    def draw(self, surface):
        if self.l_score >= 10:
            self._draw_digit(surface, self.l_score // 10,
                (Cfg.WIDTH // 2) - (Cfg.WIDTH // 3) - (Scoreboard.WIDTH * (Scoreboard.DWIDTH + 1)),
                Scoreboard.YOFFSET)
        self._draw_digit(surface, self.l_score % 10,
            (Cfg.WIDTH // 2) - (Cfg.WIDTH // 3), Scoreboard.YOFFSET)

        if self.r_score >= 10:
            self._draw_digit(surface, self.r_score // 10,
                (Cfg.WIDTH // 2) + (Cfg.WIDTH // 3), Scoreboard.YOFFSET)
        self._draw_digit(surface, self.r_score % 10,
            (Cfg.WIDTH // 2) + (Cfg.WIDTH // 3) + (Scoreboard.WIDTH * (Scoreboard.DWIDTH + 1)),
            Scoreboard.YOFFSET)

    def game_over(self):
        return self.l_score >= 11 or self.r_score >= 11

    def _get_digit(self, value):
        value *= Scoreboard.DWIDTH
        return [s[value:value + 3] for s in Scoreboard.DIGITS]
 
    def _draw_digit(self, surface, value, x, y):
        for i, row in enumerate(self._get_digit(value)):
            for j, col in enumerate(row):
                if col == "#":
                    pygame.draw.rect(surface, Const.WHITE,
                        (x + j * self.WIDTH, y + i * self.WIDTH, self.WIDTH, self.WIDTH))


class Ball(pygame.sprite.Sprite):
    def __init__(self, side, speed = 3, angle = None):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.SP_WIDTH, Cfg.SP_WIDTH))
        self.surf.fill(Const.WHITE)

        ypos = (Cfg.HEIGHT // 2) + (Cfg.SP_WIDTH // 2)
        if side == Const.LEFT:
            xpos = 2 * (Cfg.WIDTH // 3) - (Cfg.SP_WIDTH // 2)
        else:
            xpos = 1 * (Cfg.WIDTH // 3) - (Cfg.SP_WIDTH // 2)
        self.pos = pygame.math.Vector2((xpos, ypos))
        self.speed = speed

        self.rect = self.surf.get_rect()
        self.rect.bottomleft = self.pos

        if angle is None:
            # Randomly select an angle between -60 and +60 degrees
            self.angle = (random.random() * math.pi / 1.5) - (math.pi / 6.0)
            if side == Const.LEFT:
                self.angle += math.pi
        else:
            self.angle = angle

        self.prepare_stepping()

    def move(self):
        self._step_line()
        if self.pos.y <= Cfg.SP_WIDTH:
            self.angle = (2.0 * math.pi) - self.angle
            self.pos.y = Cfg.SP_WIDTH + 1
            self.prepare_stepping()
        elif self.pos.y >= Cfg.HEIGHT:
            self.angle = (2.0 * math.pi) - self.angle
            self.pos.y = Cfg.HEIGHT - 1
            self.prepare_stepping()

    def prepare_stepping(self):
        # Bresenham's line algorithm
        # https://wiki2.org/en/Bresenham%27s_line_algorithm
        self.angle = self._normalize_angle(self.angle)
        xd = self.pos.x + (math.cos(self.angle) * Cfg.WIDTH)
        yd = self.pos.y + (math.sin(self.angle) * Cfg.HEIGHT)
        self.dst = pygame.math.Vector2((xd, yd))

        print(180.0 * self.angle / math.pi)

        self.dx = int(round(abs(self.dst.x - self.pos.x)))
        self.dy = int(round(abs(self.dst.y - self.pos.y)))
        if self.dst.x < self.pos.x:
            self.dx = -self.dx
        if self.dst.y < self.pos.y:
            self.dy = -self.dy

        if abs(self.dy) > abs(self.dx):
            self.yi = -self.speed
            if self.dy < 0:
                self.yi = self.speed
                self.dy = -self.dy
            self.D = (2 * self.dy) - self.dx
        else:
            self.xi = self.speed
            if self.dx < 0:
                self.xi = -self.speed
                self.dx = -self.dx
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
        if (rads < 0.0):
            rads += 2.0 * math.pi
        elif (rads > 2.0 * math.pi):
            rads -= 2.0 * math.pi
        return rads


class Paddle(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.SP_WIDTH, Cfg.SP_HEIGHT))
        self.surf.fill(Const.WHITE)
        self.rect = self.surf.get_rect()
        self.side = side
   
        ypos = (Cfg.HEIGHT // 2) + (Cfg.SP_HEIGHT // 2)

        if side == Const.LEFT:
            self.pos = pygame.math.Vector2((Cfg.SIDE_BUFFER, ypos))
        else:
            self.pos = pygame.math.Vector2((Cfg.WIDTH - Cfg.SIDE_BUFFER - Cfg.SP_WIDTH, ypos))
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

        if self.pos.y < Cfg.SP_HEIGHT:
            self.pos.y = Cfg.SP_HEIGHT
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

    paddles = pygame.sprite.Group()
    paddles.add(l_paddle)
    paddles.add(r_paddle)

    while not scoreboard.game_over():
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
        
        displaysurface.fill(Const.BLACK)
        scoreboard.draw(displaysurface)

        for paddle in paddles:
            displaysurface.blit(paddle.surf, paddle.rect)
        displaysurface.blit(ball.surf, ball.rect)
    
        pygame.display.update()
        FramePerSec.tick(Cfg.FPS)

        for paddle in paddles:
            paddle.move()
        ball.move()

        if ball.rect.colliderect(l_paddle.rect):
            ball.pos.x = l_paddle.rect.x + Cfg.SP_WIDTH + 10
            if ball.angle > math.pi:
                ball.angle += math.pi / 2.0
            else:
                ball.angle -= math.pi / 2.0
            ball.prepare_stepping()
        elif ball.rect.colliderect(r_paddle.rect):
            ball.pos.x = r_paddle.rect.x - Cfg.SP_WIDTH - 10
            if ball.angle > math.pi:
                ball.angle -= math.pi / 2.0
            else:
                ball.angle += math.pi / 2.0
            ball.prepare_stepping()

        if ball.pos.x >= Cfg.WIDTH - Cfg.SP_WIDTH:
            scoreboard.l_score += 1
            ball = Ball(Const.RIGHT)
        elif ball.pos.x <= 0:
            scoreboard.r_score += 1
            ball = Ball(Const.LEFT)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)


if __name__ == "__main__":
    main()
