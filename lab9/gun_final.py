import math
from random import choice, randrange, random

import pygame


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x=20, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vy -= 1 #gravity
        self.x += self.vx
        self.y -= self.vy
        if self.x + self.r > WIDTH: #check vertical wall
            self.vx = (-self.vx)*0.5 #0.5 means friction effect
            self.vy = self.vy * 0.5
            self.x = WIDTH - self.r
        if self.y + self.r > HEIGHT: #check horizontal wall
            self.vy = -self.vy * 0.5
            self.vx = self.vx * 0.5
            self.y = HEIGHT - self.r



    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r,
    
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if (self.x - obj.x)**2 + (self.y - obj.y)**2 <= (self.r + obj.r)**2:
            return True
        else:
            return False


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.a = 20 #big side
        self.b = 5 #short side
        self.color = GREY

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10
        self.a = 20

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan2((event.pos[1]-450), (event.pos[0]-20))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        # FIXIT don't know how to do it
        pygame.draw.polygon(self.screen, self.color, ((20, 450), 
                                                      (20+self.a*math.cos(self.an), 450 + self.a*math.sin(self.an)), 
                                                      (20+self.a*math.cos(self.an)+self.b*math.sin(self.an), 450+self.a*math.sin(self.an)-self.b*math.cos(self.an)), 
                                                      (20+self.b*math.sin(self.an), 450-self.b*math.cos(self.an))))

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
                self.a += 1
            self.color = RED
        else:
            self.color = GREY


class Target:
    def __init__(self, screen: pygame.Surface):
        self.x = randrange(600, 780)
        self.y = randrange(300, 550)
        self.r = randrange(10, 50)
        self.v = random()*choice((-1, 1))
        self.color = RED
        self.screen = screen
        self.points = 0
        self.live = 1

    # self.points = 0
    # self.live = 1
    # FIXME: don't work!!! How to call this functions when object is created?
    # self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        pass

    def move(self):
        self.y += self.v
        if self.y+self.r >= HEIGHT:
            self.y = HEIGHT - self.r
            self.v = -self.v
        elif self.y - self.r <= 0:
            self.y = self.r
            self.v = -self.v
        

    def hit(self, points=1):
        """Попадание шарика в цель."""
        global counter, bullet
        self.points += points
        counter += 1
        text = font.render("Вы поразили мишени за " + str(bullet)+ ' выстрелов.',True, BLACK)
        bullet = 0
        self.screen.blit(text, [150, 200])
        pygame.display.flip()
        clock.tick(1)

    def draw(self):
        if self.live:
            pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r)
        else:
            pass
    def hittest(self, obj):
        if abs(self.x - obj.x) <= abs(self.r + obj.r):
            return True
        else:
            return False
        
        


pygame.init()
font = pygame.font.Font('freesansbold.ttf', 25)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
counter = 0
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
target1 = Target(screen)
target2 = Target(screen)
while target1.hittest(target2):
    target2 = Target(screen)
finished = False

while not finished:
    screen.fill(WHITE)
    TEXT = font.render(str(counter),True, BLACK)
    screen.blit(TEXT, [10, 10])
    gun.draw()
    target1.draw()
    target2.draw()
    for b in balls:
        b.draw()
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    for b in balls:
        b.move()
        if abs(b.vx) <= 0.001:
            balls.remove(b)
        if b.hittest(target1) and target1.live:
            target1.live = 0
        if b.hittest(target2) and target2.live:
            target2.live = 0
        if not target1.live and not target2.live:
            balls.clear()
            target1.hit()
            target1 = Target(screen)
            target2 = Target(screen)
            while target1.hittest(target2):
                target2 = Target(screen)
        
    gun.power_up()
    target1.move()
    target2.move()

pygame.quit()
