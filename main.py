# Bullet --> Ball
# meteor --> block
import random
from os import path

import pygame

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 745
HEIGHT = 600
FPS = 60
score = 0

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid")
clock = pygame.time.Clock()

# Загрузка всей игровой графики
background = pygame.image.load(path.join(img_dir,
                                         'background.png')).convert()
background = pygame.transform.scale(background,
                                    (WIDTH, HEIGHT))
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir,
                                         "bluepaddle.png")).convert()
block_img = pygame.image.load(path.join(img_dir,
                                        "block.png")).convert()
ball_img = pygame.image.load(path.join(img_dir,
                                       "ball.png")).convert()
lives_img = pygame.image.load(path.join(img_dir,
                                        "lives.png")).convert()
lives_img = pygame.transform.scale(lives_img,
                                   (25, 25))
lives_img.set_colorkey(WHITE)
energise_img = pygame.image.load(path.join(img_dir,
                                           'energise.png')).convert()
energise_img = pygame.transform.scale(energise_img,
                                      (50, 50))
energise_img.set_colorkey(BLACK)
interrogative_cube_img = pygame.image.load(path.join(img_dir,
                                                     'interrogative_cube.png')).convert()
interrogative_cube_img = pygame.transform.scale(interrogative_cube_img,
                                                (50, 50))
interrogative_cube_img.set_colorkey(WHITE)
quad_shoot_img = pygame.image.load(path.join(img_dir,
                                             'quad_shoot.png')).convert()
quad_shoot_img = pygame.transform.scale(quad_shoot_img,
                                        (50, 50))
quad_shoot_img.set_colorkey(BLACK)
size_potion_img = pygame.image.load(path.join(img_dir, 'size_potion.png')).convert()
size_potion_img = pygame.transform.scale(size_potion_img,
                                         (50, 50))
size_potion_img.set_colorkey(BLACK)
super_shoot_img = pygame.image.load(path.join(img_dir,
                                              'super_shoot.png')).convert()
super_shoot_img = pygame.transform.scale(super_shoot_img,
                                         (50, 50))
super_shoot_img.set_colorkey(WHITE)
super_ball_img = pygame.image.load(path.join(img_dir,
                                             'super_ball.png')).convert()
super_ball_img = pygame.transform.scale(super_ball_img,
                                        (25, 25))
super_ball_img.set_colorkey(BLACK)

powerup_images = {'energise': energise_img,
                  'interrogative_cube': interrogative_cube_img,
                  'quad_shoot': quad_shoot_img,
                  'size_potion': size_potion_img,
                  'super_shoot': super_shoot_img}

# Загрузка мелодий игры
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
shoot_sound.set_volume(0.2)
pygame.mixer.music.load(path.join(snd_dir, 'backgroundm.mp3'))
pygame.mixer.music.set_volume(0.4)
boom_sound = pygame.mixer.Sound(path.join(snd_dir, 'expl6.wav'))
boom_sound.set_volume(0.4)
powm = pygame.mixer.Sound(path.join(snd_dir, 'powm.mp3'))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        # изменяем размер платформы
        self.image = pygame.transform.scale(player_img,
                                            (104, 24))
        # убираем черный квадрат
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 1
        self.speedx = 0
        self.shoot_delay = 750
        self.last_shot = pygame.time.get_ticks()
        self.hide_timer = pygame.time.get_ticks()
        self.speed_force = pygame.time.get_ticks()
        self.size_timer = pygame.time.get_ticks()
        self.speed_force_delay = 30000
        self.speed_force_flag = False
        self.size_delay = 30000
        self.fast = 8
        self.lives = 3
        self.hidden = False
        self.super_shoot_flag = False

    def update(self):
        global count
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] and \
                self.rect.left > 0:
            self.speedx = -1 * self.fast
        if keystate[pygame.K_RIGHT] and \
                self.rect.right + 8 < WIDTH:
            self.speedx = self.fast
        self.rect.x += self.speedx

        # показать, если скрыто
        if self.hidden and pygame.time.get_ticks() - \
                self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        if keystate[pygame.K_SPACE] and \
                not self.hidden and \
                count == 0:
            self.shoot()
            self.image = pygame.transform.scale(player_img,
                                                (104, 24))
            self.rect.inflate(104, 24)
            self.image.set_colorkey(BLACK)

        # Отмена ускорения
        if self.speed_force_flag and \
                pygame.time.get_ticks() - self.speed_force > \
                self.speed_force_delay:
            self.fast = 8

        # Отмена изменения роста
        if pygame.time.get_ticks() - self.size_timer > \
                self.size_delay:
            self.image = pygame.transform.scale(player_img,
                                                (104, 24))
            self.image.set_colorkey(BLACK)
            self.rect.inflate(104, 24)

        # Супер мяч
        if self.super_shoot_flag and keystate[pygame.K_s]:
            ball = SuperShoot(self.rect.centerx, self.rect.top)
            all_sprites.add(ball)
            super_balls.add(ball)
            self.super_shoot_flag = False
            boom_sound.play()

    def shoot(self):
        global count
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            ball = Ball(self.rect.centerx, self.rect.top)
            all_sprites.add(ball)
            balls.add(ball)
            count += 1
            shoot_sound.play()

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def speed(self):
        self.speed_force = pygame.time.get_ticks()
        self.fast = 16
        self.speed_force_flag = True

    def size(self):
        choice = random.choice([0, 1, 2])
        self.size_timer = pygame.time.get_ticks()
        if choice > 0:
            self.image = pygame.transform.scale(player_img,
                                                (52, 24))
            self.rect.inflate(52, 24)
        elif choice == 0:
            self.image = pygame.transform.scale(player_img,
                                                (156, 24))
            self.rect.inflate(156, 24)
        self.image.set_colorkey(BLACK)


class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = block_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.last_row_time = pygame.time.get_ticks()
        self.new_row_time = 30000

    def update(self):
        global mob_flag
        # self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or \
                self.rect.left < -25 or \
                self.rect.right > WIDTH + 20:
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
        if pygame.time.get_ticks() - self.last_row_time \
                > self.new_row_time:
            self.step()
            mob_flag = True
            self.last_row_time = pygame.time.get_ticks()

    def step(self):
        self.rect.y += 37


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ball_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -5
        self.speedx = 5 * random.choice([-1, 1])
        self.speed_force = pygame.time.get_ticks()
        self.speed_force_delay = 30000
        self.speed_force_flag = False
        self.flag = False

    def update(self):
        global score, count
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Отражение от трех сторон и смерть за четвертой
        if self.rect.top <= 0:
            self.speedy *= -1
            shoot_sound.play()
        if self.rect.left <= 0:
            self.speedx *= -1
            shoot_sound.play()
        if self.rect.right >= WIDTH:
            self.speedx *= -1
            shoot_sound.play()
        if self.rect.top >= HEIGHT:
            self.kill()
            count -= 1
            if count == 0:
                player.lives -= 1

        # Проверка, не ударил ли мяч игрока
        if self.rect.bottom >= HEIGHT - 25 and \
                pygame.sprite.spritecollide(player, balls,
                                            False,
                                            pygame.sprite.collide_rect):
            self.speedy *= -1
            shoot_sound.play()

        # Проверка, не ударил ли мяч моба
        hits = pygame.sprite.groupcollide(mobs,
                                          balls,
                                          True, False)
        for hit in hits:
            score += 50
            self.speedy *= -1
            boom_sound.play()
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)

        # Проверка столкновений игрока и улучшения(
        # hits = pygame.sprite.spritecollide(player,
        #                                    powerups, True)
        # for hit in hits:
        #     if hit.type == 'energise':
        #         player.speed()
        #         Ball.speed()

        # Отмена ускорения
        if self.speed_force_flag and \
                pygame.time.get_ticks() - \
                self.speed_force > \
                self.speed_force_delay:
            self.speedy = self.speedy / 20
            self.speedx = self.speedx / 20
            self.speed_force_flag = False

    def speed(self):
        self.speed_force = pygame.time.get_ticks()
        self.speed_force_flag = True


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['energise',
                                   'interrogative_cube',
                                   'quad_shoot',
                                   'size_potion',
                                   'super_shoot'])
        # 'energise', 'interrogative_cube', 'quad_shoot', 'size_potion', 'super_shoot'
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # убить, если он сдвинется с нижней части экрана
        if self.rect.top > HEIGHT:
            self.kill()


class SuperShoot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # обавить картинку
        self.image = super_ball_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -3
        self.flag = False

    def update(self):
        global score
        self.rect.y += self.speedy

        # смерть за четвертой
        if self.rect.top <= 0:
            self.kill()
            boom_sound.play()

        # Проверка, не ударил ли мяч моба
        hits = pygame.sprite.groupcollide(mobs,
                                          super_balls,
                                          True, False)
        for hit in hits:
            score += 25
            boom_sound.play()
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)




def draw_text(surf, text, size, x, y):
    font = pygame.font.Font('CollectiveSBRK.ttf', size)
    text_surface = font.render(text, True, RED)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob(row):
    for x in range(0, WIDTH + 5, 69):
        for y in range(5, 42 * row, 37):
            m = Mob(x, y)
            all_sprites.add(m)
            mobs.add(m)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "ARKANOID!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
balls = pygame.sprite.Group()
powerups = pygame.sprite.Group()
super_balls = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

newmob(5)
score = 0
count = 0
mob_flag = False
pygame.mixer.music.play(loops=-1)

# Цикл игры
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        balls = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        super_balls = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        newmob(5)
        score = 0
        count = 0
        mob_flag = False
        pygame.mixer.music.play(loops=-1)

    # Держим цикл на правильной скорости
    clock.tick(FPS)

    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        game_over = True

    # Обновление
    all_sprites.update()

    # Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player,
                                       mobs, True,
                                       pygame.sprite.collide_rect)
    if hits:
        player.lives -= 1
        player.hide()

    # Проверка столкновений игрока и улучшения
    hits = pygame.sprite.spritecollide(player,
                                       powerups, True)
    for hit in hits:
        powm.play()
        if hit.type == 'energise':
            player.speed()
        if hit.type == 'interrogative_cube':
            power = random.choice(['energise',
                                   'size_potion',
                                   'super_shoot',
                                   'quad_shoot'])
            if power == 'quad_shoot':
                for i in range(2):
                    ball = Ball(player.rect.centerx,
                                player.rect.top + 3)
                    all_sprites.add(ball)
                    balls.add(ball)
                    count += 1
                for i in range(2):
                    ball = Ball(player.rect.centerx,
                                player.rect.top + 25)
                    all_sprites.add(ball)
                    balls.add(ball)
                    count += 1
            if power == 'size_potion':
                player.size()
            if power == 'super_shoot':
                player.super_shoot_flag = True
            if power == 'energise':
                player.speed()
        if hit.type == 'quad_shoot':
            for i in range(2):
                ball = Ball(player.rect.centerx,
                            player.rect.top)
                all_sprites.add(ball)
                balls.add(ball)
                count += 1
            for i in range(2):
                ball = Ball(player.rect.centerx,
                            player.rect.top + 25)
                all_sprites.add(ball)
                balls.add(ball)
                count += 1
        if hit.type == 'size_potion':
            player.size()
        if hit.type == 'super_shoot':
            player.super_shoot_flag = True

    # Движение стенки
    if mob_flag:
        newmob(1)
        mob_flag = False
    # Если игрок умер, игра окончена
    if player.lives == 0:
        game_over = True

    # Отрисовка
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_lives(screen, WIDTH - 100, 5,
               player.lives,
               lives_img)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()
