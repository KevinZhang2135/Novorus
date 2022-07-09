import pygame
import random
import os
import math

RED = (211, 47, 47)
BLOOD_RED = (198, 40, 40)

YELLOW = (255, 231, 45)
GOLD = (255, 219, 14)

GREY = (188, 188, 188)
DARK_GREY = (168, 168, 168)
BLACK = (50, 50, 50)

BROWN = (131, 106, 83)
PECAN = (115, 93, 71)
DARK_BROWN = (104, 84, 66)


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

    def custom_draw(self, player, show_hitboxes=False):
        '''Draws the screen according to player movement'''
        self.center_target(player)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.bottom):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if show_hitboxes:
                hitbox = pygame.Rect(
                    sprite.rect.x - self.offset.x,
                    sprite.rect.y - self.offset.y,
                    sprite.rect.width,
                    sprite.rect.height)

                pygame.draw.rect(
                    self.display_surface,
                    (255, 0, 0),
                    hitbox,
                    1)


class Menu(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = [
            pygame.display.get_surface().get_height() * 3 / 32] * 2

        menu_width = self.display_surface.get_height() / 3

        self.menu_sprites = {
            'menu': load_image(
                os.path.join('sprites/menu', 'menu.png'),
                (self.width, self.height)),

            'paused': load_image(
                os.path.join('sprites/menu', 'paused.png'),
                (self.width, self.height))}

        self.image = self.menu_sprites['menu']

        self.rect = self.image.get_rect(
            bottomright=[self.display_surface.get_width(),
                         self.display_surface.get_height()])

        self.menu_rect = pygame.Rect(
            (self.display_surface.get_width() - menu_width) / 2,
            (self.display_surface.get_height() - menu_width) / 2,
            menu_width,
            menu_width)

        # menu text
        self.menu_text = load_text(
            'Menu',
            (self.menu_rect.centerx, self.menu_rect.top + self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            BLACK)

        # exit text
        self.yellow_exit_text = self.draw_exit_text(YELLOW)
        self.black_exit_text = self.draw_exit_text(BLACK)
        self.exit_text = self.black_exit_text
        self.pressed = False

    def draw_exit_text(self, color):
        exit_text, exit_text_rect = load_text(
            'Exit',
            (self.menu_rect.centerx, self.menu_rect.bottom - self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            color)

        return exit_text, exit_text_rect

    def update(self):
        global game_state

        pause_left_click = (pygame.mouse.get_pressed()[0]
                            and self.rect.collidepoint(pygame.mouse.get_pos()))

        escape_key = pygame.key.get_pressed()[pygame.K_ESCAPE]

        # checks for left click and escape_key to popup menu
        if (pause_left_click or escape_key) and not self.pressed:
            self.pressed = True
            game_state['paused'] = not game_state['paused']

        elif not (pause_left_click or escape_key) and self.pressed:
            self.pressed = False

        if game_state['paused']:
            self.image = self.menu_sprites['menu']

            pygame.draw.rect(
                self.display_surface,
                BROWN,
                self.menu_rect)

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.menu_rect,
                5)

            self.display_surface.blit(*self.menu_text)
            self.display_surface.blit(*self.exit_text)

            if self.exit_text[1].collidepoint(pygame.mouse.get_pos()):
                self.exit_text = self.yellow_exit_text
                if pygame.mouse.get_pressed()[0]:
                    game_state['runtime'] = False

            else:
                self.exit_text = self.black_exit_text

        else:
            self.image = self.menu_sprites['menu']


class Bar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width = pygame.display.get_surface().get_height() / 16
        self.height = pygame.display.get_surface().get_height() / 16

        self.bar_width = self.width * 1.5
        self.bar_height = self.display_surface.get_height() / 64
        self.coords = coords

    def set_health(self):
        self.image = load_image(
            os.path.join('sprites/menu', 'heart.png'),
            (self.width, self.height))

        self.create_bar()

        self.light_color = RED
        self.dark_color = BLOOD_RED

    def set_speed(self):
        self.image = load_image(
            os.path.join('sprites/menu', 'lightning.png'),
            (self.width, self.height))

        self.create_bar()

        self.light_color = YELLOW
        self.dark_color = GOLD

    def set_attack(self):
        self.image = load_image(
            os.path.join('sprites/menu', 'sword.png'),
            (self.width, self.height))

        self.create_bar()

        self.light_color = GREY
        self.dark_color = DARK_GREY

    def create_bar(self):
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

        self.lost_bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

        self.text_center = self.bar.center

    def draw(self, text, ratio=1):
        self.bar.width = self.bar_width * ratio

        if ratio < 1:
            pygame.draw.rect(self.display_surface,
                             PECAN, self.lost_bar, 2)

        pygame.draw.rect(self.display_surface, self.light_color, self.bar)
        pygame.draw.rect(self.display_surface, self.dark_color, self.bar, 2)

        self.display_surface.blit(
            *load_text(
                text,
                self.text_center,
                self.bar.height,
                BLACK))


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
        pygame.draw.rect(self.display_surface, BROWN, self.rect)
        pygame.draw.rect(self.display_surface, DARK_BROWN, self.rect, 5)

        health_ratio = target.health['current'] / target.health['total']
        text = [f"{target.speed['current']}",
                f"{target.attack['current']}"]

        for index, bar in enumerate(self.bars[1:]):
            bar.draw(text[index])

        self.health_bar.draw(
            f"{target.health['current']} / {target.health['total']}",
            health_ratio)

        self.display_surface.blit(
            *load_text(
                f'{target.name}',
                (self.coords.x + self.width / 2, self.coords.y +
                 self.display_surface.get_height() * 3 / 128),
                self.display_surface.get_height() / 32,
                BLACK))


class Player(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(
            os.path.join('sprites/player/idle', 'knight_idle1.png'),
            (self.width, self.height))

        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.in_combat = False
        self.attacking = False
        self.exp = [0, 10]

        self.action = 'idle'
        self.facing = 'right'
        self.name = 'Player'

        self.animation_cooldown = 500
        self.animation_time = pygame.time.get_ticks()

        self.frame = 0
        self.level = 1
        self.move_speed = 5
        self.move = pygame.math.Vector2(0, 0)

        self.bonuses = {'health': 0,
                        'speed': 0,
                        'attack': 0}

        self.health = {'current': 100,
                       'total': 100,
                       'base': 100}

        self.speed = {'current': 10,
                      'total': 10,
                      'base': 10}

        self.attack = {'current': 20,
                       'total': 20,
                       'base': 20}

        self.set_stats()

        self.animation_types = {'idle': [],
                                'run': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/player/{type}'))
            for i in range(num_of_frames):
                image = load_image(
                    os.path.join(
                        f'sprites/player/{type}', f'knight_{type}{i + 1}.png'),
                    (self.width, self.height))

                self.animation_types[type].append(image)

    def set_stats(self):
        stats = {'health': self.health,
                 'speed': self.speed,
                 'attack': self.attack}

        for type in stats:
            ratio = stats[type]['current'] / stats[type]['total']

            stats[type]['total'] = round(stats[type]['base']
                                         * (1 + self.bonuses[type])
                                         * (1.05**(self.level - 1)))

            stats[type]['current'] = round(ratio * stats[type]['total'])

    def movement(self):
        '''Handles movement'''
        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            # creates movement using falsy and truthy values that evaluate to 0 and 1
            self.move = pygame.math.Vector2(right - left, down - up)
            if self.move.length_squared() > 0:  # checks if the player is moving
                # converts the coordinates to a vector according to the radius
                self.move.scale_to_length(self.move_speed)

            
            self.rect.centerx += self.move.x
            self.rect.centery += self.move.y

    def collision(self):
        '''Handles collision'''
        global collision_group

        for sprite in collision_group:
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

    def attack_enemy(self):
        global enemies

        
        # checks if the player rect overlaps an enemy rect
        if pygame.sprite.spritecollide(self, enemies, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask):
                for enemy in enemies:
                    # determines which enemy is withing the player rect
                    if pygame.Rect.colliderect(player.rect, enemy.rect):
                        if not self.in_combat and self.health['current'] > 0 and enemy.health['current'] > 0:
                            self.in_combat = True
                            self.animation_time = pygame.time.get_ticks()
                            self.frame = 0

                            enemy.in_combat = True
                            enemy.animation_time = pygame.time.get_ticks()
                            enemy.frame = 0

                            # player faces enemy
                            if self.rect.centerx < enemy.rect.centerx:
                                self.facing = 'right'
                                enemy.facing = 'left'

                            else:
                                self.facing = 'left'
                                enemy.facing = 'right'

                        if self.in_combat:
                            if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
                                self.attacking = True
                                self.frame = 0
                            
                            # only deal damage when animation ends
                            if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                                if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
                                    enemy.health['current'] -= self.attack['current']

                                    if enemy.health['current'] <= 0:
                                        enemy.health['current'] = 0
                                        enemy.in_combat = False
                                        enemy.kill()
                                        del enemy

                                        self.in_combat = False
                                        self.animation_time = pygame.time.get_ticks()
                                        self.frame = 0

                        else:
                            # player dies
                            pass
                        break
                            
    def animation(self):
        '''Handles animation'''
        if not self.in_combat:
            if self.move.length_squared() > 0:
                self.action = 'run'

                if self.move.x < 0:
                    self.facing = 'left'

                elif self.move.x > 0:
                    self.facing = 'right'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        # set image
        self.image = self.animation_types[self.action][self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1 

            # loops frames
            if self.frame >= len(self.animation_types[self.action]):
                self.frame = 0

        # reflect image if facing left
        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy()
        self.animation()


class Ghost(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(
            os.path.join('sprites/ghost/idle', 'ghost_idle1.png'),
            (self.width, self.height))

        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.in_combat = False
        self.attacking = False

        self.attack_cooldown = 250
        self.attack_time = pygame.time.get_ticks()
        self.animation_cooldown = 400
        self.animation_time = pygame.time.get_ticks()

        self.frame = 0
        self.level = random.randint(1, 2)
        self.exp = 10 * self.level

        self.action = 'idle'
        self.facing = random.choice(['left', 'right'])
        self.name = 'Ghost'

        health = round(30 * (1.1**(self.level - 1)))
        self.health = {'current': health,
                       'total': health}

        attack = round(10 * (1.1**(self.level - 1)))
        self.attack = {'current': attack,
                       'total': attack}

        speed = round(6 * (1.1**(self.level - 1)))
        self.speed = {'current': speed,
                      'total': speed}

        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/ghost/{type}'))
            for i in range(num_of_frames):
                image = load_image(
                    os.path.join(
                        f'sprites/ghost/{type}', f'ghost_{type}{i + 1}.png'),
                    (self.width, self.height))

                self.animation_types[type].append(image)

    def attack_enemy(self):
        global player
        global player_group

        if self.in_combat:
            if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
                self.attacking = True
                self.frame = 0
            
            # only deal damage when animation ends
            if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
                    player.health['current'] -= self.attack['current']

                    if player.health['current'] <= 0:
                        player.health['current'] = 0
                        player.in_combat = False

                        self.in_combat = False
                        self.animation_time = pygame.time.get_ticks()
                        self.frame = 0

        else:
            # ghost dies
            pass
                    
    def animation(self):
        '''Handles animation'''
        if not self.in_combat:
            self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        self.image = self.animation_types[self.action][self.frame]
        if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1

            if self.frame >= len(self.animation_types[self.action]):
                self.frame = 0

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        '''Handles events'''
        self.attack_enemy()
        self.animation()


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.chest_sprites = {
            'closed': load_image(
                os.path.join('sprites', 'chest_closed.png'),
                (self.width, self.height)),

            'opened': load_image(
                os.path.join('sprites', 'chest_opened.png'),
                (self.width, self.height)), }

        self.image = self.chest_sprites['closed']

        self.rect = self.image.get_rect(center=coords)

        self.opened = False

    def collision(self):
        global player
        collision_distance = pygame.math.Vector2((self.rect.width + player.rect.width) / 2,
                                                 (self.rect.height + player.rect.height) / 2)

        distance = pygame.math.Vector2(self.rect.centerx - player.rect.centerx,
                                       self.rect.centery - player.rect.centery)

        # checks if the distance of the sprites are within collision distance
        if (abs(distance.x) - 1 < collision_distance.x
            and abs(distance.y) - 1 < collision_distance.y
                and not self.opened):

            self.image = self.chest_sprites['opened']
            self.opened = True

            player.bonuses['health'] += 1
            player.bonuses['attack'] += 1
            player.set_stats()

    def update(self):
        self.collision()


class Ambience(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, image: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(image, size)
        self.rect = self.image.get_rect(center=coords)

        if random.randint(0, 1):
            self.image = pygame.transform.flip(self.image, True, False)


def load_image(image, size: list):
    '''Loads an image according to the input'''
    image = pygame.image.load(image).convert_alpha()
    image = pygame.transform.scale(image, [round(i) for i in size])

    return image


def load_text(text, coords, text_size, color):
    # "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0
    font = pygame.font.Font('comicoro.ttf', round(text_size))
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=coords)

    return text, text_rect


game_state = {'paused': True,
              'runtime': True,
              'fullscreen': True}

pygame.init()
pygame.font.init()
pygame.display.set_caption('Novorus')

# sets the size of the screen; defaults to full screen
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

player_group = pygame.sprite.GroupSingle()
camera_group = CameraGroup()
enemies = pygame.sprite.Group()
collision_group = pygame.sprite.Group()
hud_group = CameraGroup()

# hud
menu = Menu(hud_group)
player_bars = TargetBars((0, 0), (player_group, hud_group))
enemy_bars = TargetBars((0, screen.get_height() * 11 / 64), hud_group)

# player
player = Player((0, 0), (75, 75), camera_group)

# ambience
wall = Ambience((100, 100), (100, 100), 'sprites/wall1.png',
                (camera_group, collision_group))

used_coords = [(0, 0), (100, 100)]
coords = None

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
        os.path.join('sprites/ambience', f'{obj}{variation}.png'),
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

while game_state['runtime']:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            game_state['runtime'] = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitboxes=False)

    # checks if the player rect is within an enemy rect
    for enemy in enemies:
        # determines which enemy is withing the player rect
        if enemy.in_combat:
            enemy_bars.add_sprites(hud_group)
            enemy_bars.draw(enemy)
            break
            
        else:
            enemy_bars.hide_sprites()

    # redraws sprites and images
    player_bars.draw(player)
    hud_group.draw(screen)
    
    
    # updates
    if not game_state['paused']:
        camera_group.update()

    hud_group.update()

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()


#