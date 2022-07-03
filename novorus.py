from re import T
import pygame
import os
import math
import random

# "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0

def load_image(image, size: list):
    '''Loads an image according to the input'''
    image = pygame.image.load(os.path.join(
        'sprites', image)).convert_alpha()
    image = pygame.transform.scale(image, size)

    return image

def load_text(text, coords, text_size, color):
    font = pygame.font.Font('comicoro.ttf', round(text_size))
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=coords)

    return text, text_rect


class CameraGroup(pygame.sprite.Group):
    def __init__(self, ):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_size()[0] / 2
        self.half_height = self.display_surface.get_size()[1] / 2

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def custom_draw(self, player, show_hitbox=False):
        '''Draws the screen according to player movement'''
        self.center_target(player)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.bottom):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if show_hitbox:
                rectingle = pygame.Rect(
                    sprite.rect.x - self.offset.x,
                    sprite.rect.y - self.offset.y,
                    sprite.rect.width,
                    sprite.rect.height)

                pygame.draw.rect(
                    self.display_surface,
                    (255, 0, 0),
                    rectingle,
                    1)

#self.display_surface = pygame.display.get_surface()
class Player(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size
        
        self.image = load_image('knight_walk1.png', size)
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.colliding = False
        self.in_combat = False
        self.attacking = False

        self.facing = 'right'
        self.name = 'Player'

        self.bonuses = {'health': 0,
                        'speed': 0,
                        'attack': 0}

        self.health = {'current': 100,
                       'total': 100}

        self.speed = {'current': 30,
                      'total': 30}

        self.attack = {'current': 20,
                       'total': 20}

        self._level = 1
        self.level = self._level
        self.move_speed = 5
        self.ticks = 0

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value

        for status in self.health:
            self.health[status] = round(self.health[status]
                                        * (1 + self.bonuses['health'])
                                        * (1.05**(self._level - 1)))

        for status in self.speed:
            self.speed[status] = round(self.speed[status]
                                       * (1 + self.bonuses['speed'])
                                       * (1.05**(self._level - 1)))

        for status in self.attack:
            self.attack[status] = round(self.attack[status]
                                        * (1 + self.bonuses['attack'])
                                        * (1.05**(self._level - 1)))

    def movement(self):
        '''Handles movement'''
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        up = keys[pygame.K_UP] or keys[pygame.K_w]

        # creates movement using falsy and truthy values that evaluate to 0 and 1
        move = pygame.math.Vector2(right - left, down - up)
        if move.length_squared() > 0:  # checks if the player is moving
            # converts the coordinates to a vector according to the radius
            move.scale_to_length(self.move_speed)

        if not self.in_combat:
            self.rect.centerx += move.x
            self.rect.centery += move.y

    def collision(self, sprites):
        '''Handles collision'''
        for sprite in sprites:
            collision_distance = pygame.math.Vector2((self.rect.width + sprite.rect.width) / 2,
                                                     (self.rect.height + sprite.rect.height) / 2)

            distance = pygame.math.Vector2(self.rect.centerx - sprite.rect.centerx,
                                           self.rect.centery - sprite.rect.centery)

            # checks if the distance of the sprites are within collision distance
            if (abs(distance.x) + self.width / 6 < collision_distance.x
                and abs(distance.y) + self.height / 6 < collision_distance.y):

                # horizontal collision
                if abs(distance.x) > abs(distance.y):
                    # left collision
                    if distance.x > 0:
                        self.rect.left = sprite.rect.right - self.width / 6

                    # right collision
                    if distance.x < 0:
                        self.rect.right = sprite.rect.left + self.width / 6

                # vertical collision
                elif abs(distance.y) > abs(distance.x):
                    # bottom collision
                    if distance.y < 0:
                        self.rect.bottom = sprite.rect.top + self.height / 6

                    # top collision
                    if distance.y > 0:
                        self.rect.top = sprite.rect.bottom - self.height / 6

    def animation(self):
        '''Handles animation'''
        movement_sprites = ['knight_walk1.png',
                            'knight_walk2.png',
                            'knight_walk1.png',
                            'knight_walk3.png']

        idle_sprites = ['knight_walk1.png',
                        'knight_idle1.png',
                        'knight_walk1.png',
                        'knight_idle2.png']

        combat_sprites = ['knight_walk1.png',
                          'knight_attack1.png',
                          'knight_attack2.png',
                          'knight_attack3.png']

        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            if left or right or down or up:
                self.image = load_image(
                    movement_sprites[math.floor(self.ticks / 30)], 
                    (self.width, self.height))

                if left:
                    self.facing = 'left'

                elif right:
                    self.facing = 'right'

            else:
                self.image = load_image(
                    idle_sprites[math.floor(self.ticks / 30)],
                    (self.width, self.height))

        else:
            if self.attacking:
                self.image = load_image(
                    combat_sprites[math.floor((self.ticks - 20) / 25)],
                    (self.width, self.height))

            else:
                self.image = load_image(
                    idle_sprites[math.floor(self.ticks / 30)],
                    (self.width, self.height))

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player, collision_group):
        '''Handles events'''
        self.movement()
        self.collision(collision_group)
        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0


class Ghost(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size
        
        self.image = load_image('ghost_idle1.png', size)
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.in_combat = False
        self.attacking = False

        self.move_speed = 2
        self.ticks = random.randint(0, 30)
        self.level = random.randint(1, 2)

        self.facing = random.choice(['left', 'right'])
        self.name = 'Ghost'

        health = round(30 * (1.1**(self.level - 1)))
        self.health = {'current': health,
                       'total': health}

        attack = round(10 * (1.1**(self.level - 1)))
        self.attack = {'current': attack,
                       'total': attack}

        speed = round(15 * (1.1**(self.level - 1)))
        self.speed = {'current': speed,
                      'total': speed}

    def animation(self):
        '''Handles animation'''
        idle_sprites = ['ghost_idle1.png',
                        'ghost_idle2.png',
                        'ghost_idle3.png',
                        'ghost_idle2.png']

        combat_sprites = ['ghost_idle1.png',
                          'ghost_attack1.png',
                          'ghost_attack2.png',
                          'ghost_attack3.png']

        if not self.in_combat:
            self.image = load_image(
                idle_sprites[math.floor(self.ticks / 30)], 
                (self.width, self.height))

        else:
            if self.attacking:
                self.image = load_image(
                    combat_sprites[math.floor((self.ticks - 40) / 25)], 
                    (self.width, self.height))

            else:
                self.image = load_image(
                    idle_sprites[math.floor(self.ticks / 30)], 
                    (self.width, self.height))

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player, collision_group):
        '''Handles events'''
        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0


class Ambience(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, image: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(image, size)
        self.rect = self.image.get_rect(center=coords)

        if random.randint(0, 1):
            self.image = pygame.transform.flip(self.image, True, False)


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image('chest_closed.png', size)
        self.rect = self.image.get_rect(center=coords)

        self.opened = False

    def collision(self, player):
        collision_distance = pygame.math.Vector2((self.rect.width + player.rect.width) / 2,
                                                 (self.rect.height + player.rect.height) / 2)

        distance = pygame.math.Vector2(self.rect.centerx - player.rect.centerx,
                                       self.rect.centery - player.rect.centery)

        # checks if the distance of the sprites are within collision distance
        if (abs(distance.x) - 1 < collision_distance.x
            and abs(distance.y) - 1 < collision_distance.y
                and not self.opened):

            self.image = load_image(
                'chest_opened.png',
                (self.width, self.height))

            self.opened = True
            player.level += 1

    def update(self, player, collision_group):
        self.collision(player)


class Menu(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = [pygame.display.get_surface().get_height() * 3 / 32] * 2
        menu_width = self.display_surface.get_height() / 3

        self.image = load_image('menu1.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            bottomright=[self.display_surface.get_width(),
                         self.display_surface.get_height()])

        self.menu_rect = pygame.Rect(
            (self.display_surface.get_width() - menu_width) / 2,
            (self.display_surface.get_height() - menu_width) / 2,
            menu_width,
            menu_width)

        # menu text
        self.menu_text, self.menu_text_rect = load_text(
            'Menu',
            (self.menu_rect.centerx, self.menu_rect.top + self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            (50, 50, 50))

        # exit text
        self.draw_exit_text((50, 50, 50))
        self.pressed = False

    def draw_exit_text(self, color):
        self.exit_text, self.exit_text_rect = load_text(
            'Exit',
            (self.menu_rect.centerx, self.menu_rect.bottom - self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            color)

    def draw(self):
        global paused

        if paused:
            pygame.draw.rect(
                self.display_surface,
                (131, 106, 83),
                self.menu_rect)

            pygame.draw.rect(
                self.display_surface,
                (104, 84, 66),
                self.menu_rect,
                5)

            self.display_surface.blit(self.menu_text, self.menu_text_rect)
            self.display_surface.blit(self.exit_text, self.exit_text_rect)

    def update(self):
        global paused
        global runtime

        pause_left_click = (pygame.mouse.get_pressed()[0]
                            and self.rect.collidepoint(pygame.mouse.get_pos()))

        escape_key = pygame.key.get_pressed()[pygame.K_ESCAPE]

        # checks for left click and escape_key to popup menu
        if (pause_left_click or escape_key) and not self.pressed:
            self.pressed = True
            paused = not paused

        elif not (pause_left_click or escape_key) and self.pressed:
            self.pressed = False

        if paused:
            self.image = load_image('menu2.png', (self.width, self.height))

            if self.exit_text_rect.collidepoint(pygame.mouse.get_pos()):
                self.draw_exit_text((255, 231, 45))
                if pygame.mouse.get_pressed()[0]:
                    runtime = False

            else:
                self.draw_exit_text((50, 50, 50))

        else:
            self.image = load_image('menu1.png', (self.width, self.height))


class Bar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = [pygame.display.get_surface().get_height() / 16] * 2
        self.bar_height = self.display_surface.get_height() / 64
        self.coords = coords

    def draw(self, text):
        pygame.draw.rect(self.display_surface, self.light_color, self.bar, 0)
        pygame.draw.rect(self.display_surface, self.dark_color, self.bar, 3)

        self.display_surface.blit(
            *load_text(
                text,
                self.bar.center,
                self.bar.height,
                (50, 50, 50)))

    def bar_rect(self):
        bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.rect.width * 1.5,
            self.bar_height)

        return bar

    def set_health(self):
        self.image = load_image('heart.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = self.bar_rect()

        self.light_color = (211, 47, 47)
        self.dark_color = (198, 40, 40)

    def set_speed(self):
        self.image = load_image('lightning.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = self.bar_rect()

        self.light_color = (255, 231, 45)
        self.dark_color = (255, 219, 14)

    def set_attack(self):
        self.image = load_image('sword.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = self.bar_rect()

        self.light_color = (188, 188, 188)
        self.dark_color = (168, 168, 168)


class TargetBars: 
    def __init__(self, coords: list, groups):
        self.display_surface = pygame.display.get_surface()

        self.coords = pygame.math.Vector2(coords)
        self.width = self.display_surface.get_height() * 9 / 64
        self.height = self.display_surface.get_height() * 11 / 64

        self.health_bar = Bar(
            (self.coords.x,  self.display_surface.get_height()
             * 4 / 128 + self.coords.y),
            groups)

        self.speed_bar = Bar(
            (self.coords.x, self.display_surface.get_height()
             * 9 / 128 + self.coords.y),
            groups)

        self.attack_bar = Bar(
            (self.coords.x, self.display_surface.get_height()
             * 14 / 128 + self.coords.y),
            groups)

        self.bars = [self.health_bar, self.speed_bar, self.attack_bar]

        self.health_bar.set_health()
        self.speed_bar.set_speed()
        self.attack_bar.set_attack()

        self.rect = pygame.Rect(coords, (self.width, self.height))

    def hide_sprites(self):
        for bar in self.bars:
            bar.kill()
            
    def add_sprites(self, group):
        for bar in self.bars:
            group.add(bar)

    def draw(self, target):
        pygame.draw.rect(self.display_surface, (131, 106, 83), self.rect)
        pygame.draw.rect(self.display_surface, (104, 84, 66), self.rect, 5)

        text = [f"{target.health['current']} / {target.health['total']}",
                f"{target.speed['current']}",
                f"{target.attack['current']}"]

        for index, bar in enumerate(self.bars):
            bar.draw(text[index])

        self.display_surface.blit(
            *load_text(
                f'{target.name}',
                (self.coords.x + self.width / 2, self.coords.y +
                 self.display_surface.get_height() * 3 / 128),
                self.display_surface.get_height() / 32,
                (50, 50, 50)))


def combat(player, enemy):
    # checks health before entering combat
    if player.health['current'] > 0 or enemy.health['current'] > 0:
        # sync ticks so combat immediately starts
        if not player.in_combat:
            player.in_combat = True
            enemy.in_combat = True

            player.ticks = 0

        # player and enemy face each other
        if player.rect.centerx < enemy.rect.centerx:
            player.facing = 'right'
            enemy.facing = 'left'

        else:
            player.facing = 'left'
            enemy.facing = 'right'

        # player animation for attacking
        if player.ticks == 0:
            chance = random.randint(
                0, player.speed['current'] + enemy.speed['current'])
            if chance < player.speed['current']:
                # player attacks
                player.attacking = True
                player.ticks =  20

            else:
                # enemy attacks
                enemy.attacking = True
                enemy.ticks = 40

        # only deal damage after end of animation
        if player.ticks == 119 and player.attacking:
            enemy.health['current'] -= player.attack['current']
            player.attacking = False

        elif enemy.ticks == 119 and enemy.attacking:
            player.health['current'] -= enemy.attack['current']
            enemy.attacking = False

    # end of combat
    if player.health['current'] <= 0 or enemy.health['current'] <= 0:
        player.in_combat = False
        player.attacking = False

        enemy.in_combat = False
        enemy.attacking = False

        if enemy.health['current'] <= 0:
            enemy.kill()
            del enemy

        else:
            pass


pygame.init()
pygame.font.init()
pygame.display.set_caption('Novorus')

# sets the size of the screen; defaults to full screen
screen = pygame.display.set_mode((1920, 1020), pygame.RESIZABLE)
clock = pygame.time.Clock()

camera_group = CameraGroup()
enemies = pygame.sprite.Group()
collision_group = pygame.sprite.Group()
hud_group = CameraGroup()

# hud
menu = Menu(hud_group)
player_bars = TargetBars((0, 0), hud_group)
enemy_bars = TargetBars((0, screen.get_height() * 11 / 64), hud_group)

# player
player = Player((0, 0), (75, 75), camera_group)

used_coords = [(0, 0)]
coords = None

wall = Ambience((100, 100), (100, 100), 'wall1.png', (camera_group, collision_group))

# ambience
size = (60, 40, 125, 100)
objects = ['rock', 'grass', 'tree']
for j in range(150):
    obj = random.choice(objects)
    while coords in used_coords or not coords:
        coords = [round(random.randint(-1500, 1500), -2) for i in range(2)]

    used_coords.append(coords)
    groups = [camera_group]
    variation = random.randint(1, 3)

    decor = Ambience(
        coords,
        [size[objects.index(obj)]] * 2,
        f'{obj}{variation}.png',
        groups)

# enemies
for i in range(20):
    while coords in used_coords or not coords:
        coords = [round(random.randint(-1500, 1500), -2) for i in range(2)]

    used_coords.append(coords)
    ghost = Ghost(coords, (60, 60), (camera_group, enemies))

# chests
for i in range(5):
    while coords in used_coords or not coords:
        coords = [round(random.randint(-1500, 1500), -2) for i in range(2)]

    used_coords.append(coords)
    chest = Chest(coords, (60, 60), (camera_group, collision_group))

ticks = 0
paused = True
runtime = True
fullscreen = True

while runtime:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            runtime = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitbox=True)

    # updates

    # checks if the player rect is within an enemy rect
    if pygame.sprite.spritecollide(player, enemies, False):
        # checks if the player mask overlaps an enemy mask
        if pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask):
            for enemy in enemies:
                # determines which enemy is withing the player rect
                if pygame.Rect.colliderect(player.rect, enemy.rect):
                    combat(player, enemy)
                    if player.in_combat:
                        enemy_bars.add_sprites(hud_group)
                        enemy_bars.draw(enemy)

                    break

    if not player.in_combat:
        enemy_bars.hide_sprites()

    if not paused:
        camera_group.update(player, collision_group)

    hud_group.update()

    # hud
    menu.draw()
    player_bars.draw(player)
    hud_group.draw(screen)

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()


#
