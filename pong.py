import sys
import math
import random
import pygame
from pygame.locals import *


class Cfg():
    HEIGHT = 450            # pixels
    WIDTH = 600             # pixels
    SP_WIDTH = 15           # pixels
    SP_HEIGHT = 60          # pixels
    PD_MOVE = 5             # pixels
    SIDE_BUFFER = 40        # pixels
    FPS = 60                # frames per second


class Const():
    LEFT = 0
    RIGHT = 1
    WHITE = (255,255,255)
    BLACK = (0,0,0)


class Scoreboard():
    WIDTH = 5               # pixels
    DWIDTH = 3              # character columns
    DHEIGHT = 5             # character rows
    YOFFSET = 10            # pixels
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
            self.__draw_digit(surface, self.l_score // 10, (Cfg.WIDTH // 2) - (Cfg.WIDTH // 3) - (Scoreboard.WIDTH * (Scoreboard.DWIDTH + 1)), Scoreboard.YOFFSET)
        self.__draw_digit(surface, self.l_score % 10,      (Cfg.WIDTH // 2) - (Cfg.WIDTH // 3), Scoreboard.YOFFSET)

        if self.r_score >= 10:
            self.__draw_digit(surface, self.r_score // 10, (Cfg.WIDTH // 2) + (Cfg.WIDTH // 3), Scoreboard.YOFFSET)
        self.__draw_digit(surface, self.r_score % 10,      (Cfg.WIDTH // 2) + (Cfg.WIDTH // 3) + (Scoreboard.WIDTH * (Scoreboard.DWIDTH + 1)), Scoreboard.YOFFSET)

    def game_over(self):
        return self.l_score >= 11 or self.r_score >= 11

    def __get_digit(self, value):
        value *= Scoreboard.DWIDTH
        return [s[value:value + 3] for s in Scoreboard.DIGITS]
 
    def __draw_digit(self, surface, value, x, y):
        for i, row in enumerate(self.__get_digit(value)):
            for j, col in enumerate(row):
                if col == "#":
                    pygame.draw.rect(surface, Const.WHITE,
                        (x + j * self.WIDTH, y + i * self.WIDTH, self.WIDTH, self.WIDTH))

class Ball(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.SP_WIDTH, Cfg.SP_WIDTH))
        self.surf.fill(Const.WHITE)
        self.rect = self.surf.get_rect()

        xpos = (Cfg.WIDTH  // 2) - (Cfg.SP_WIDTH // 2)
        ypos = (Cfg.HEIGHT // 2) + (Cfg.SP_WIDTH // 2)

        self.pos = pygame.math.Vector2((xpos, ypos))
        self.rect.bottomleft = self.pos

        # Randomly select an angle between -45 and 45 degrees
        self.angle = (random.random() * math.pi / 4.0) - (math.pi / 8.0)
        if side == Const.LEFT:
            self.angle += math.pi

        self.dx = 0
        self.dy = 0
        self.xi = 0
        self.yi = 0
        self.D  = 0

        self.prepare_stepping()

    def move(self):
        self.step_line()

        if self.pos.y < Cfg.SP_WIDTH:
            self.angle = self.angle + (math.pi / 4.0)
            self.pos.y = Cfg.SP_WIDTH
            self.prepare_stepping()
        elif self.pos.y > Cfg.HEIGHT:
            self.angle = self.angle - math.pi
            self.pos.y = Cfg.HEIGHT
            self.prepare_stepping()

    def prepare_stepping(self):
        # Bresenham's line algorithm
        # https://wiki2.org/en/Bresenham%27s_line_algorithm
        xd = self.pos.x + math.cos(self.angle) * Cfg.WIDTH
        yd = self.pos.y + math.sin(self.angle) * Cfg.HEIGHT
        destination = pygame.math.Vector2((xd, yd))

        if abs(destination.y - self.pos.y) < abs(destination.x - self.pos.x):
            if self.pos.x > destination.x:
                self.dx = self.pos.x - destination.x
                self.dy = self.pos.y - destination.y
            else:
                self.dx = destination.x - self.pos.x
                self.dy = destination.y - self.pos.y

            self.yi = 1
            if self.dy < 0:
                self.yi = -1
                self.dy = -self.dy
            self.D = (2 * self.dy) - self.dx
        else:
            if self.pos.y > destination.y:
                self.dx = self.pos.x - destination.x
                self.dy = self.pos.y - destination.y
            else:
                self.dx = destination.x - self.pos.x
                self.dy = destination.y - self.pos.y

            self.xi = 1
            if self.dx < 0:
                self.xi = -1
                self.dx = -self.dx
            self.D = (2 * self.dx) - self.dy

    def step_line(self):
        if abs(self.dy) < abs(self.dx):
            self.step_line_low()
        else:
            self.step_line_high()
        self.rect.bottomleft = self.pos

    def step_line_low(self):
        if self.dx > 0:
            self.pos.x += 1
        elif self.dx < 0:
            self.pos.x -= 1

        if self.D > 0:
            self.pos.y += self.yi
            self.D += 2 * (self.dy - self.dx)
        else:
            self.D += 2 * self.dy

    def step_line_high(self):
        if self.dy > 0:
            self.pos.y += 1
        elif self.dy < 0:
            self.pos.y -= 1

        if self.D > 0:
            self.pos.x += self.xi
            self.D += 2 * (self.dx - self.dy)
        else:
            self.D += 2 * self.dx


class Paddle(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__() 
        self.surf = pygame.Surface((Cfg.SP_WIDTH, Cfg.SP_HEIGHT))
        self.surf.fill((255,255,255))
        self.rect = self.surf.get_rect()
   
        ypos = (Cfg.HEIGHT // 2) + (Cfg.SP_HEIGHT // 2)

        self.side = side
        if side == Const.LEFT:
            self.pos = pygame.math.Vector2((Cfg.SIDE_BUFFER, ypos))
        else:
            self.pos = pygame.math.Vector2((Cfg.WIDTH - Cfg.SIDE_BUFFER - Cfg.SP_WIDTH, ypos))
        self.rect.bottomleft = self.pos

    def move(self):
        pressed_keys = pygame.key.get_pressed()
            
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
                break
        
        displaysurface.fill(Const.BLACK)
        scoreboard.draw(displaysurface)

        for padddle in paddles:
            displaysurface.blit(padddle.surf, padddle.rect)
        displaysurface.blit(ball.surf, ball.rect)
    
        pygame.display.update()
        FramePerSec.tick(Cfg.FPS)

        for paddle in paddles:
            paddle.move()
        ball.move()

        if pygame.sprite.spritecollideany(ball, paddles):
            if ball.rect.colliderect(l_paddle.rect):
                ball.angle = math.pi - ball.angle
                ball.pos.x += 2
            else:
                ball.angle = ball.angle + (math.pi / 2.0)
                ball.pos.x -= 2
            ball.prepare_stepping()
            ball.move()

        if ball.pos.x >= Cfg.WIDTH - Cfg.SP_WIDTH:
            scoreboard.l_score += 1
            ball = Ball(Const.LEFT)
        elif ball.pos.x <= 0:
            scoreboard.r_score += 1
            ball = Ball(Const.RIGHT)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
