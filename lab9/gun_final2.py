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
GAME_COLORS = [BLUE, YELLOW, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class Gamelead:
    """Объект, обрабатывающий все происходящее на экране


    Variables:

    finished (int): 0 при нормальном ходе игры, 1 - закрывает окно

    balls (list): массив шаров, нарисованных на экране в данный момент

    counter (int): счетчик числа выигранных раундов

    bullet (int): число выпущенных пуль на данный момент

    screen (pygame.Surface): объект, отвечающий за отрисовку всех других объектов (экран)

    clock (pygame.time.Clock): объект, отвечающий за FPS и временные промежутки

    gun (Gun): пушка игрока

    enemy (Enemy): вражеская пушка

    events (list): массив пользовательских событий. events[0]-поворот вражеской пушки, events[1]-выстрел вражеской пушки

    target_easy (Target): мишень с предсказуемым движение

    target_hard (Target): мишень с более сложным движением
    """

    def __init__(self):
        self.finished = 0
        self.balls = []
        self.counter = 0
        self.bullet = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.gun = Gun(self.screen)
        self.enemy = Enemy(self.screen)
        self.events = [pygame.event.Event(0), pygame.event.Event(1)]
        pygame.time.set_timer(self.events[0], 1000)
        self.clock.tick(
            500
        )  # разница по времени между поворотом и стрельбой вражеской пушки
        pygame.time.set_timer(self.events[1], 1000)
        self.target_easy = Target(self.screen)
        self.target_hard = Target(self.screen, color=GREEN, vx=randrange(-5, 5))
        while self.target_easy.hittest(
            self.target_hard
        ):  # гарантирует, что цели не сгенерируются друг в друге
            self.target_easy = Target(self.screen)

    def draw0(self):
        """Отрисовка объектов в начале кадра"""
        self.screen.fill(WHITE)
        TEXT = FONT.render(str(self.counter), True, BLACK)  # рендер строки
        self.screen.blit(TEXT, [10, 10])  # вывод строки на экран
        self.gun.draw()
        self.enemy.draw()
        self.target_easy.draw()
        self.target_hard.draw()
        for b in self.balls:
            b.draw()

    def time(self):
        """Ограничивает FPS. Вызывается каждый кадр"""
        self.clock.tick(FPS)

    def handle_event(self, event):
        """Обработчик событий

        Args:

        event (pygame.event.Event): событие, нуждающееся в обработке
        """
        if event.type == pygame.QUIT:
            self.finished = 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.gun.fire2_start()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            self.gun.fire1()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            self.gun.targetting(event)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            self.gun.v = 7
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            self.gun.v = -7
        elif event.type == pygame.KEYUP and (event.key == pygame.K_LEFT):
            self.gun.v = 0
        elif event.type == pygame.KEYUP and (event.key == pygame.K_RIGHT):
            self.gun.v = 0
        elif event.type == lead.events[0].type:
            self.enemy.turn()
        elif event.type == lead.events[1].type:
            self.enemy.fire()

    def handle_balls(self):
        """Отдельный обработчик столкновения шаров с целями"""
        for b in self.balls:
            b.move()
            if abs(b.vx) <= 0.001:  # шары, которые почти остановились - исчезают
                self.balls.remove(b)
            if isinstance(b, EnemyBall) and b.hittest(
                self.gun
            ):  # вражеский снаряд убивает пушку игрока
                pygame.quit()
            if b.hittest(self.target_easy) and self.target_easy.live:
                self.target_easy.live = 0
            if b.hittest(self.target_hard) and self.target_hard.live:
                self.target_hard.live = 0
            if not self.target_easy.live and not self.target_hard.live:
                self.balls.clear()
                self.target_easy.hit()
                self.target_easy = Target(self.screen)
                self.target_hard = Target(self.screen, color=GREEN, vx=randrange(-5, 5))
                while self.target_easy.hittest(self.target_hard):
                    self.target_easy = Target(self.screen)

    def end_frame(self):
        """Завершение кадра"""
        self.gun.power_up()
        self.gun.move()
        self.target_easy.move()
        self.target_hard.move()

    def add_ball(self, ball):
        """Работа с массивом шаров balls

        Args:

        ball (Ball): шар, который нужно добавить"""
        self.balls.append(ball)

    def count(self, delta_counter=0, delta_bullet=0):
        """Работа с глобальными счетчиками

        Args:

        delta_counter (int): на сколько увеличить counter

        delta_bullet (int): на сколько увеличить bullet"""
        self.counter += delta_counter
        self.bullet += delta_bullet


class Ball:
    """Обычный снаряд

    Variables:

    screen: экран, на котором происходит отрисовка

    x: положение по горизонтали

    y: положение по вертикали

    r: радиус шара

    vx: скорость шара по горизонтали

    vy: скорость шара по вертикали

    color: цвет шара
    """

    def __init__(self, screen: pygame.Surface, x=20, y=450, r=10, vx=0, vy=0):
        self.screen = screen
        self.x = x
        self.y = y
        self.r = r
        self.vx = vx
        self.vy = vy
        self.color = choice(GAME_COLORS)

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vy -= 1  # гравитация
        self.x += self.vx
        self.y -= self.vy
        if self.x + self.r > WIDTH:  # столкновение с вертикальной стеной
            self.vx = (-self.vx) * 0.5  # трение
            self.vy = self.vy * 0.5
            self.x = WIDTH - self.r
        if self.y + self.r > HEIGHT:  # столкновение с горизонтальной стеной
            self.vy = -self.vy * 0.5
            self.vx = self.vx * 0.5
            self.y = HEIGHT - self.r

    def draw(self):
        """Отрисовка шара"""
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r,
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение. Должен иметь аргументы x, y, r
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 <= (self.r + obj.r) ** 2:
            return True
        else:
            return False


class Cball(Ball):
    """Особый снаряд пушки игрока, выпускаемый нажатием кнопки F на клавиатуре. Игнорирует гравитацию, но летит медленно

    Методы наследуются из Ball"""

    def __init__(self, screen, x=20, y=450, vx=0, vy=0):
        super().__init__(screen, x, y)
        self.vx = vx
        self.vy = vy
        self.r = 5
        self.color = BLACK

    def move(self):
        self.x += self.vx
        self.y -= self.vy

    def draw(self):
        super().draw()

    def hittest(self, obj):
        return super().hittest(obj)


class Gun:
    """Пушка игрока

    Variables:

    f2_power (int): мощность пушки, увеличивающаяся при зарядке и определяющая скорость вылета снаряда

    f2_on (int): 1 если пушка заряжается в данный момент, иначе 0

    an (float): угол поворота пушки относительно горизонтали

    a, b (int): размеры пушки

    v(int): скорость пушки вдоль горизонтали
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.f2_power: int = 10
        self.f2_on = 0
        self.an: float = 1
        self.a: int = 20  # big side
        self.b: int = 5  # short side
        self.color: int = GREY
        self.x: int = 20  # coord of gun
        self.y: int = 450
        self.r = (self.a + self.b) / 2  # for compatibility with hittest
        self.v: int = 0  # velocity

    def fire2_start(self):
        """Отметка о начале процесса зарядки пушки игрока"""
        self.f2_on = 1

    def fire1(self):
        """Выстрел cball по направлению пушки. Происходит нажатием кнопки F на клавиатуре"""
        new_cball = Cball(
            self.screen,
            vx=2 * math.cos(self.an),
            vy=-2 * math.sin(self.an),
            x=self.x,
            y=self.y,
        )
        lead.add_ball(new_cball)
        lead.count(delta_bullet=1)

    def fire2_end(self, event):
        """Выстрел обычным снарядом по направлению пушки.

        Происходит при отпускании кнопки мыши.
        Скорость вылета зависит от того, сколько заряжалась пушка.
        """
        lead.count(delta_bullet=1)
        new_ball = Ball(
            self.screen,
            x=self.x,
            y=self.y,
            r=15,
            vx=self.f2_power * math.cos(self.an),
            vy=-self.f2_power * math.sin(self.an),
        )
        self.an = math.atan2((event.pos[1] - new_ball.y), (event.pos[0] - new_ball.x))
        lead.add_ball(new_ball)
        self.f2_on = 0
        self.f2_power = 10  # сбросить заряд
        self.a = 20

    def targetting(self, event):
        """Прицеливание в направление мыши"""
        if event:
            self.an = math.atan2((event.pos[1] - self.y), (event.pos[0] - self.x))
        if self.f2_on:
            self.color = YELLOW
        else:
            self.color = GREY

    def draw(self):
        """Отрисовка пушки игрока. Зависит от угла поворота an"""
        pygame.draw.polygon(
            self.screen,
            self.color,
            (
                (self.x, self.y),
                (
                    self.x + self.a * math.cos(self.an),
                    self.y + self.a * math.sin(self.an),
                ),
                (
                    self.x + self.a * math.cos(self.an) + self.b * math.sin(self.an),
                    self.y + self.a * math.sin(self.an) - self.b * math.cos(self.an),
                ),
                (
                    self.x + self.b * math.sin(self.an),
                    self.y - self.b * math.cos(self.an),
                ),
            ),
        )

    def power_up(self):
        """Процесс зарядки пушки. Вызывается каждый кадр"""
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
                self.a += 1
            self.color = YELLOW
        else:
            self.color = GREY

    def move(self):
        """Движение по горизонтали. Происходит стрелками вправо и влево"""
        self.x += self.v


class Enemy(Gun):
    """Вражеская пушка. Наследует Gun"""

    def __init__(self, screen):
        super().__init__(screen)
        self.color = RED
        self.x = 400
        self.y = 100
        self.an = 0
        self.f2_power = 7

    def draw(self):
        super().draw()

    def turn(self):
        """Поворот вражеской пушки на случайный угол раз в секунду.

        Угол находится строго в диапазоне, при котором в пушку игрока все еще возможно попасть
        """
        self.an = math.pi / 2 + random() * math.atan(380 / 350) * choice(
            (-1, 1)
        )  # angle from which we see possible coordinates of gun

    def fire(self):
        """Выстрел вражеской пушки. Происходит вслед за ее поворотом"""
        new_enemyball = EnemyBall(
            self.screen,
            x0=self.x,
            y0=self.y,
            vx=self.f2_power * math.cos(self.an),
            vy=-self.f2_power * math.sin(self.an),
        )
        lead.add_ball(new_enemyball)


class EnemyBall(Ball):
    """Снаряды вражеской пушки. Наследует Ball

    Не взаймодействует с Target, но способны убить пушку игрока"""

    def __init__(self, screen, x0, y0, vx=0, vy=0):
        super().__init__(screen, x=x0, y=y0)
        self.vx = vx
        self.vy = vy
        self.color = BLACK

    def move(self):
        super().move()

    def draw(self):
        super().draw()

    def hittest(self, obj):
        if isinstance(obj, Target):
            return False  # enemyball can't hit Target
        return super().hittest(obj)


class Target:
    """Цель, которую нужно сбить

    Variables:

    live(int): 0 если цель подбили, иначе 1
    """

    def __init__(self, screen: pygame.Surface, color=RED, vx=0):
        self.x = randrange(600, 780)
        self.y = randrange(300, 550)
        self.r = randrange(10, 50)
        self.v = random() * choice((-1, 1))
        self.vx = vx
        self.color = color
        self.screen = screen
        self.live = 1

    def move(self):
        """Движение цели. Логика столкновений со стенами"""
        self.y += self.v
        self.x += self.vx

        if self.y + self.r >= HEIGHT:
            self.y = HEIGHT - self.r
            self.v = -self.v
        elif self.y - self.r <= 0:
            self.y = self.r
            self.v = -self.v
        elif self.x + self.r >= WIDTH:
            self.x = WIDTH - self.r
            self.vx = -self.vx
        elif self.x - self.r <= 0:
            self.x = self.r
            self.vx = -self.vx

    def hit(self):
        """Попадание шарика в цель. Вывод надписи. Пауза на 1 секунду"""

        text = FONT.render(
            "Вы поразили мишени за " + str(lead.bullet) + " выстрелов.", True, BLACK
        )
        lead.count(delta_counter=1, delta_bullet=-lead.bullet)
        self.screen.blit(text, [150, 200])
        pygame.display.flip()
        lead.clock.tick(1)

    def draw(self):
        """Отрисовка цели"""
        if self.live:
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)
        else:
            pass

    def hittest(self, obj):
        """Проверка на столкновение с объектом obj"""
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 <= (self.r + obj.r) ** 2:
            return True
        else:
            return False


pygame.init()
FONT = pygame.font.Font("freesansbold.ttf", 25)
lead = Gamelead()

while not lead.finished:
    lead.draw0()
    pygame.display.update()

    lead.time()
    for event in pygame.event.get():
        lead.handle_event(event)
    lead.handle_balls()
    lead.end_frame()
pygame.quit()
