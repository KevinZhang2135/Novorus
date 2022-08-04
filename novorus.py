import pygame
import random
import os
import csv

RED = (211, 47, 47)
BLOOD_RED = (198, 40, 40)

ORANGE = (255, 174, 66)
TANGERINE = (212, 103, 0)

MELLOW_YELLOW = (255, 229, 134)
YELLOW = (255, 231, 45)
GOLD = (255, 219, 14)

WHITE = (255, 255, 255)
LIGHT_GREY = (210, 210, 210)
GREY = (188, 188, 188)
DARK_GREY = (168, 168, 168)
BLACK = (50, 50, 50)

BROWN = (131, 106, 83)
PECAN = (115, 93, 71)
DARK_BROWN = (104, 84, 66)


class Level:
    def __init__(self, floor_level, tile_size):
        self.tile_size = tile_size
        self._floor_level = floor_level

        self.display_surface = pygame.display.get_surface()
        self.read_csv_level()

    @property
    def floor_level(self):
        return self._floor_level

    @floor_level.setter
    def floor_level(self, value):
        self._floor_level = value
        self.clear_level()
        self.read_csv_level()

    def read_csv_level(self):
        files = os.listdir(f'levels/{self._floor_level}')
        for path in files:
            with open(os.path.join(f'levels/{self._floor_level}', path)) as file:
                csv_file = csv.reader(file)
                self.create_tile_group(csv_file, path[0:-4])

    def clear_level(self):
        global camera_group, player_group

        for sprite in camera_group.sprites():
            if sprite not in player_group:
                sprite.kill()
                del sprite

    def create_tile_group(self, csv_file, type):
        create_tile = {'player': self.set_player_coords,
                       'wall': self.add_walls,
                       'enemies': self.add_enemies,
                       'chest': self.add_chests,
                       'static_decor': self.add_static_decor,
                       'animated_decor': self.add_animated_decor,
                       'exit': self.add_exit}

        static_decoration = ['grass', 'rock', 'tree']
        animated_decoration = ['torch',]

        for row_index, row in enumerate(csv_file):
            for col_index, id in enumerate(row):
                id = int(id)
                if id != -1:
                    x = col_index * self.tile_size
                    y = row_index * self.tile_size

                    if type in static_decoration:
                        create_tile['static_decor'](id, type, (x, y))

                    elif type in animated_decoration:
                        create_tile['animated_decor'](id, type, (x, y))

                    else:
                        create_tile[type](id, (x, y))

    def set_player_coords(self, id, coords):
        global player

        player.rect.center = coords

    def add_walls(self, id, coords):
        global camera_group, collision_group

        images = ['grey_bricks/brick_top.png',
                  'grey_bricks/brick_middle.png',
                  'grey_bricks/brick_bottom.png',
                  'grey_bricks/brick_pile.png',
                  'grey_bricks/brick_side.png']

        wall = StaticTile(
            coords,
            (self.tile_size, self.tile_size),
            os.path.join('sprites/walls', images[id]),
            (camera_group, collision_group))

    def add_enemies(self, id, coords):
        global camera_group, enemy_group, light_group

        enemies = [Ghost,
                   Mimic]
        enemies[id](coords, (60, 60), self.floor_level, (camera_group, enemy_group))

    def add_chests(self, id, coords):
        global camera_group, collision_group

        chest = Chest(
            coords,
            (self.tile_size * 0.6, self.tile_size * 0.6),
            (camera_group, collision_group))

    def add_static_decor(self, id, type, coords):
        global camera_group

        images = {'grass': ['grass1.png',
                            'grass2.png',
                            'grass3.png'],

                  'rock': ['rock1.png',
                           'rock2.png',
                           'rock3.png',
                           'rock4.png'],

                  'tree': ['tree1.png',
                           'tree2.png',
                           'tree3.png']}

        sprite_size = {'grass': 0.3,
                       'rock': 0.6,
                       'tree': 1.5}

        size = round(self.tile_size 
                     * 0.8
                     * randomize(sprite_size[type] * 100, 0.1)
                     / 100)

        decor = StaticTile(
            coords,
            [size] * 2,
            os.path.join(f'sprites/decoration/{type}', images[type][id]),
            camera_group)

        decor.rect.centerx += random.randint(-25, 25)
        decor.rect.centery += random.randint(-25, 25)

        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

    def add_animated_decor(self, id, type, coords):
        global camera_group, light_group

        sprite_size = {'torch': 0.7}
        size = round(self.tile_size 
                     * 0.8
                     * randomize(sprite_size[type] * 100, 0.1)
                     / 100)

        animation_sprites = []
        num_of_frames = len(os.listdir(f'sprites/decoration/{type}'))
        for i in range(num_of_frames):
            image = load_image(
                os.path.join(
                    f'sprites/decoration/{type}', f'{type}{i + 1}.png'),
                [size] * 2)

            animation_sprites.append(image)

        decor = AnimatedTile(
            coords,
            [size] * 2,
            animation_sprites,
            (camera_group, light_group))

        if type == 'torch':
            decor.rect.centerx += random.randint(-1, 1) * 25
            decor.rect.centery += 25

    def add_exit(self, id, coords):
        global camera_group

        exit = LevelExit(
            coords, [round(self.tile_size * 0.8)] * 2, camera_group)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2

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


class LightSources(pygame.sprite.Group):
    def __init__(self, resolution):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.resolution = resolution

        self.light_size = pygame.math.Vector2(500, 500)
        self.light = load_image(
            os.path.join('sprites/light', 'soft_circle.png'),
            self.light_size)

        self.light = color_image(self.light, MELLOW_YELLOW)
        self.filter = pygame.surface.Surface(self.resolution)

        # light offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2

    def offset_lights(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def render_lighting(self, player):
        global level
    
        self.offset_lights(player)
        if level.floor_level > 1:
            self.filter.fill(DARK_GREY)

        else:
            self.filter.fill(LIGHT_GREY)
        
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft \
                         - self.offset \
                         + list(map(lambda x: x / 2, sprite.rect.size)) \
                         - self.light_size / 2
            
            self.filter.blit(self.light, offset_pos)

        self.display_surface.blit(
            self.filter, 
            (0, 0), 
            special_flags=pygame.BLEND_RGBA_MULT)


class Menu(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 100, 100
        menu_width = 350

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
            self.image = self.menu_sprites['paused']

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


class Text:
    def __init__(self, text, rect):
        self.text = text
        self.rect = rect

        self.time = pygame.time.get_ticks()
        self.acceleration = -0.1
        self.velocity = random.randint(1250, 2000) / 1000 + 1.5


class PopUpText:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.texts = []
        self.offset = pygame.math.Vector2()

    def center_target(self, player):
        self.offset.x = player.rect.centerx - self.display_surface.get_width() / 2
        self.offset.y = player.rect.centery - self.display_surface.get_height() / 2

    def add_text(self, text, coords, size, color):
        text = Text(*load_text(text, coords, size, color))
        self.texts.append(text)

    def move_text(self, text):
        '''Moves the text vertically'''
        if text.velocity > 0:
            text.rect.y -= text.velocity
            text.velocity += text.acceleration

    def custom_draw(self, player):
        '''Draws the text according to player movement'''
        self.center_target(player)
        expired_texts = []

        for index, text in enumerate(self.texts):
            if pygame.time.get_ticks() - text.time > 1000:
                expired_texts.append(index)

            self.move_text(text)
            offset_pos = text.rect.topleft - self.offset
            self.display_surface.blit(text.text, offset_pos)

        # removes texts that have remained on the screen
        expired_texts.sort(reverse=True)
        for index in expired_texts:
            expired_text = self.texts.pop(index)
            del expired_text


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.coords = coords

        self.width, self.height = 60, 60

        self.bar_width = self.width * 1.7
        self.bar_height = 15

        self.image = load_image(
            os.path.join('sprites/menu', 'heart.png'),
            (self.width, self.height))

        self.rect = self.image.get_rect(topleft=self.coords)
        self.bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

        self.total_bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

    def draw(self, target):
        ratio = target.health['current'] / target.health['total']
        self.bar.width = self.bar_width * ratio

        pygame.draw.rect(self.display_surface, PECAN, self.total_bar, 2)
        pygame.draw.rect(self.display_surface, RED, self.bar)
        pygame.draw.rect(self.display_surface, BLOOD_RED, self.bar, 2)

        self.display_surface.blit(
            *load_text(
                target.health['current'],
                self.total_bar.center,
                self.bar.height,
                BLACK))


class SpeedBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.coords = coords

        self.width, self.height = 60, 60
        self.bar_width = self.width * 1.7
        self.bar_height = 15

        self.image = load_image(
            os.path.join('sprites/menu', 'lightning.png'),
            (self.width, self.height))

        self.rect = self.image.get_rect(topleft=self.coords)
        self.bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

    def draw(self, target):
        pygame.draw.rect(self.display_surface, YELLOW, self.bar)
        pygame.draw.rect(self.display_surface, GOLD, self.bar, 2)

        self.display_surface.blit(
            *load_text(
                target.speed['current'],
                self.bar.center,
                self.bar.height,
                BLACK))


class AttackBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.coords = coords

        self.width, self.height = 60, 60

        self.bar_width = self.width * 1.7
        self.bar_height = 15

        self.image = load_image(
            os.path.join('sprites/menu', 'sword.png'),
            (self.width, self.height))

        self.rect = self.image.get_rect(topleft=self.coords)
        self.bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

    def draw(self, target):
        pygame.draw.rect(self.display_surface, GREY, self.bar)
        pygame.draw.rect(self.display_surface, DARK_GREY, self.bar, 2)

        self.display_surface.blit(
            *load_text(
                target.attack['current'],
                self.bar.center,
                self.bar.height,
                BLACK))


class Bars(pygame.sprite.Group):
    def __init__(self, coords):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.coords = pygame.math.Vector2(coords)

        self.width = 150
        self.height = 200
        self.rect = pygame.Rect(self.coords, (self.width, self.height))

        self.exp_width = self.width * 0.5
        self.exp_height = self.height * 0.2
        self.exp_rect = pygame.Rect(self.coords, (self.exp_width, self.exp_height))


    def custom_draw(self, targets):
        if len(targets.sprites()) > 0:
            if len(targets.sprites()) > 1:
                for target in targets:
                    if (target.in_combat or target.rect.collidepoint(Cursor.offset_mouse_pos())):
                        break

                    else:
                        target = False

            else:
                target = targets.sprites()[0]

            if target and target.show_stats:
                pygame.draw.rect(self.display_surface, BROWN, self.rect)
                pygame.draw.rect(self.display_surface, DARK_BROWN, self.rect, 5)
                
                name_text, name_text_rect = load_text(
                    f'{target.name} lvl {target.level}',
                    (self.coords.x + self.width / 2,
                     self.coords.y + self.height * 0.15),
                    self.height * 0.125,
                    BLACK)

                self.display_surface.blit(name_text, name_text_rect)

                for sprite in self.sprites():
                    sprite.draw(target)
                    self.display_surface.blit(sprite.image, sprite.coords)

                if name_text_rect.collidepoint(pygame.mouse.get_pos()):
                    exp_text, exp_text_rect = load_text(
                        f'exp {target.exp}',
                        self.exp_rect.center,
                        self.exp_height * 0.75,
                        BLACK)

                    self.exp_rect.width = exp_text_rect.width + 20
                    self.exp_rect.topleft = pygame.mouse.get_pos()

                    pygame.draw.rect(self.display_surface, BROWN, self.exp_rect)
                    pygame.draw.rect(self.display_surface, DARK_BROWN, self.exp_rect, 3)
                    self.display_surface.blit(exp_text, exp_text_rect)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, tile_size, group):
        super().__init__(group)

        self.display_surface = pygame.display.get_surface()
        self.tile_size = tile_size
        self.image = load_image(
            os.path.join('sprites/menu', 'cursor.png'),
            (100, 100))

        self.rect = self.image.get_rect(center=(0, 0))

    def update(self):
        global player

        coords = self.offset_mouse_pos()
        coords[0] = round(coords[0] / tile_size) * tile_size
        coords[0] -= player.rect.centerx - self.display_surface.get_width() / 2

        coords[1] = round(coords[1] / tile_size) * tile_size
        coords[1] -= player.rect.centery - self.display_surface.get_height() / 2

        self.rect.center = coords

    @staticmethod
    def offset_mouse_pos():
        global player

        display_surface = pygame.display.get_surface()
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += player.rect.centerx - display_surface.get_width() / 2
        mouse_pos[1] += player.rect.centery - display_surface.get_height() / 2

        return mouse_pos


class Player(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = True

        self.action = 'idle'
        self.facing = 'right'
        self.name = 'Player'

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 350
        self.attack_cooldown = 275
        self.cooldown = self.animation_cooldown

        self.frame = 0
        self.crit_chance = 0.05

        self.exp = 0
        self.exp_levels = [i for i in range(100, 10000, 100)]
        self.level = 1
        while self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_velocity = 7

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

        self.image = self.animation_types['idle'][self.frame]

        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

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
            self.acceleration = pygame.math.Vector2(right - left, down - up)
            if self.acceleration.length_squared() > 0:  # checks if the player is moving
                # converts the coordinates to a vector according to the radius
                self.acceleration.scale_to_length(self.max_velocity)
                self.velocity += self.acceleration
                self.velocity *= 0.5

            else:
                self.velocity *= 0.8

            if abs(self.velocity.x) < 0.25:
                self.velocity.x = 0

            if abs(self.velocity.y) < 0.25:
                self.velocity.y = 0

            self.rect.centerx += self.velocity.x
            self.rect.centery += self.velocity.y

    def collision(self):
        '''Handles collision'''
        global collision_group

        for sprite in collision_group:
            margin = pygame.math.Vector2(self.width / 8, self.height / 2.5)

            collision_distance = pygame.math.Vector2((self.rect.width + sprite.rect.width) / 2,
                                                     (self.rect.height + sprite.rect.height) / 2)

            distance = pygame.math.Vector2(self.rect.centerx - sprite.rect.centerx,
                                           self.rect.centery - sprite.rect.centery)

            # checks if the distance of the sprites are within collision distance
            if (abs(distance.x) + margin.x <= collision_distance.x
                and abs(distance.y) + margin.y <= collision_distance.y):

                # horizontal collision
                if abs(distance.x) + margin.x > abs(distance.y) + margin.y:
                    # left collision
                    if distance.x > 0 and self.velocity.x < 0:
                        self.rect.left = sprite.rect.right - margin.x

                    # right collision
                    elif distance.x < 0 and self.velocity.x > 0:
                        self.rect.right = sprite.rect.left + margin.x

                    self.velocity.x = 0

                # vertical collision
                if abs(distance.y) + margin.y > abs(distance.x) + margin.x:
                    # bottom collision
                    if distance.y < 0 and self.velocity.y > 0:
                        self.rect.bottom = sprite.rect.top + margin.y

                    # top collision
                    elif distance.y > 0 and self.velocity.y < 0:
                        self.rect.top = sprite.rect.bottom - margin.y

                    self.velocity.y = 0

    def attack_enemy(self):
        global enemy_group

        # checks if the player rect overlaps an enemy rect
        if pygame.sprite.spritecollide(self, enemy_group, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, enemy_group, False, pygame.sprite.collide_mask):
                for enemy in enemy_group:
                    # determines which enemy is within the player rect
                    if pygame.Rect.colliderect(player.rect, enemy.rect):
                        if not self.in_combat and self.health['current'] > 0 and enemy.health['current'] > 0:
                            self.in_combat = True
                            self.animation_time = pygame.time.get_ticks()
                            self.frame = 0

                            enemy.show_stats = True
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
                            self.cooldown = self.attack_cooldown

                            # attack animation
                            if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.cooldown:
                                self.attacking = True
                                self.frame = 0

                            # checks if the animation ended
                            if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                                # only deal damage when attack cooldown ends
                                if pygame.time.get_ticks() - self.animation_time > self.cooldown:
                                    dodge_chance = random.randint(
                                        0,
                                        5 * (enemy.speed['current'] + self.speed['current']))

                                    enemy_coords = [
                                        random.randint(
                                            round(
                                                (enemy.rect.left + enemy.rect.centerx) / 2),
                                            round((enemy.rect.right + enemy.rect.centerx) / 2)),
                                        enemy.rect.top]

                                    if dodge_chance > enemy.speed['current']:
                                        # randomizes damage between 0.9 and 1.1
                                        damage = randomize(
                                            self.attack['current'], 0.15)

                                        # doubles damage if crit
                                        crit = random.randint(
                                            0, 100) / 100 <= self.crit_chance
                                        if crit:
                                            damage *= 2
                                            pop_up_text.add_text(
                                                damage, enemy_coords, 35, TANGERINE)

                                        else:
                                            pop_up_text.add_text(
                                                damage, enemy_coords, 30, ORANGE)

                                        enemy.health['current'] -= damage

                                    else:
                                        pop_up_text.add_text(
                                            'Dodged', enemy_coords, 20, GOLD)

                                    if enemy.health['current'] <= 0:
                                        player.exp += enemy.exp

                                        enemy.health['current'] = 0
                                        enemy.in_combat = False
                                        enemy.animation_time = pygame.time.get_ticks()
                                        enemy.cooldown = enemy.animation_cooldown
                                        enemy.kill()
                                        del enemy

                                        self.in_combat = False
                                        self.animation_time = pygame.time.get_ticks()
                                        self.cooldown = self.animation_cooldown
                        break

    def animation(self):
        '''Handles animation'''
        if not self.in_combat:
            if self.velocity.length_squared() > 0:
                self.action = 'run'

                if self.velocity.x < 0:
                    self.facing = 'left'

                elif self.velocity.x > 0:
                    self.facing = 'right'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        # loops frames
        if self.frame >= len(self.animation_types[self.action]):
            self.frame = 0

        # set image
        self.image = self.animation_types[self.action][self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1

        # reflect image if facing left
        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def leveling_up(self):
        '''Increases player level when they reach exp cap'''
        if self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy()
        self.animation()
        self.leveling_up()


class GenericEnemy:
    def attack_enemy(self):
        global player

        if self.in_combat:
            self.cooldown = self.attack_cooldown
            if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.cooldown:
                self.attacking = True
                self.frame = 0

            # only deal damage when animation ends
            if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                if pygame.time.get_ticks() - self.animation_time > self.cooldown:
                    dodge_chance = random.randint(
                        0, 5 * (player.speed['current'] + self.speed['current']))

                    player_coords = [
                        random.randint(
                            round((player.rect.left + player.rect.centerx) / 2),
                            round((player.rect.right + player.rect.centerx) / 2)),
                        player.rect.top]

                    if dodge_chance > player.speed['current']:
                        # randomizes damage between 0.9 and 1.1
                        damage = randomize(self.attack['current'], 0.15)

                        # doubles damage if crit
                        crit = random.randint(0, 100) / 100 <= self.crit_chance
                        if crit:
                            damage *= 2
                            pop_up_text.add_text(
                                damage, player_coords, 35, BLOOD_RED)

                        else:
                            pop_up_text.add_text(
                                damage, player_coords, 30, RED)

                        player.health['current'] -= damage

                    else:
                        pop_up_text.add_text('Dodged', player_coords, 20, GOLD)

                    if player.health['current'] <= 0:
                        player.health['current'] = 0
                        player.in_combat = False
                        player.animation_time = pygame.time.get_ticks()
                        player.cooldown = player.animation_cooldown

                        self.in_combat = False
                        self.animation_time = pygame.time.get_ticks()
                        self.cooldown = self.animation_cooldown

        if self.health['current'] < 0:
            # enemy dies
            self.in_combat = False
            self.cooldown = self.animation_cooldown

    def animation(self):
        '''Handles animation'''
        if not self.in_combat:
            self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        # loops frames
        if self.frame >= len(self.animation_types[self.action]):
            self.frame = 0

        # set image
        self.image = self.animation_types[self.action][self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1

        # reflects over y-axis if facing left
        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)


class Ghost(pygame.sprite.Sprite, GenericEnemy):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = True

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = randomize(400, 0.2)
        self.attack_cooldown = 300
        self.cooldown = self.animation_cooldown

        self.frame = 0
        self.crit_chance = 0.05
        self.exp = 15
        self.level = level

        self.action = 'idle'
        self.facing = random.choice(['left', 'right'])
        self.name = 'Ghost'

        self.health = {'current': round(30 * (1.1**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(10 * (1.1**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(6 * (1.1**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/enemies/ghost/{type}'))
            for i in range(num_of_frames):
                image = load_image(
                    os.path.join(
                        f'sprites/enemies/ghost/{type}',
                        f'ghost_{type}{i + 1}.png'),
                    (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        '''Handles events'''
        self.attack_enemy()
        self.animation()


class Mimic(pygame.sprite.Sprite, GenericEnemy):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1000
        self.attack_cooldown = 300
        self.cooldown = self.animation_cooldown

        self.frame = 0
        self.crit_chance = 0.05
        self.exp = 50
        self.level = level

        self.action = 'idle'
        self.facing = random.choice(['left', 'right'])
        self.name = 'Mimic'

        self.health = {'current': round(100 * (1.2**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(20 * (1.15**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(7 * (1.05**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/enemies/mimic/{type}'))
            for i in range(num_of_frames):
                image = load_image(
                    os.path.join(
                        f'sprites/enemies/mimic/{type}',
                        f'mimic_{type}{i + 1}.png'),
                    (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

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
                os.path.join('sprites/chest', 'chest_closed.png'),
                (self.width, self.height)),

            'opened': load_image(
                os.path.join('sprites/chest', 'chest_opened.png'),
                (self.width, self.height)), }

        self.image = self.chest_sprites['closed']
        self.rect = self.image.get_rect(center=coords)
        self.opened = False

    def collision(self):
        global player

        # checks if the distance of the sprites are within collision distance
        if pygame.Rect.colliderect(self.rect, player.rect) and not self.opened:
            self.image = self.chest_sprites['opened']
            self.opened = True

            player.exp += 10
            player.bonuses['health'] += 0.05
            player.bonuses['speed'] += 0.1
            player.bonuses['attack'] += 0.05
            player.set_stats()

    def update(self):
        self.collision()


class LevelExit(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(
            os.path.join('sprites/exit', 'dirt_hole.png'),
            size)

        self.rect = self.image.get_rect(center=coords)

    def update(self):
        global player_group, level

        if pygame.sprite.spritecollide(self, player_group, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, player_group, False, pygame.sprite.collide_mask):
                level.floor_level += 1


class StaticTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, image: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(image, size)
        self.rect = self.image.get_rect(center=coords)


class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, images: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 250
        self.frame = 0

        self.animation_types = images
        self.image = self.animation_types[self.frame]
        self.rect = self.image.get_rect(center=coords)

    def animation(self):
        '''Handles animation'''
        # loops frames
        if self.frame >= len(self.animation_types):
            self.frame = 0

        # set image
        self.image = self.animation_types[self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1

    def update(self):
        self.animation()


def load_image(image, size: list):
    '''Loads an image according to the input'''
    image = pygame.image.load(image).convert_alpha()
    image = pygame.transform.scale(image, [round(i) for i in size])

    return image


def load_text(text, coords, text_size, color):
    # "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0
    font = pygame.font.Font('comicoro.ttf', round(text_size))
    # pygame.font.Font.set_bold(font, 1) # creates a bold font if the boolean is true

    text = font.render(str(text), True, color)
    text_rect = text.get_rect(center=coords)

    return text, text_rect


def randomize(value: int, offset: float):
    return random.randint(
        round(value * (1 - offset)),
        round(value * (1 + offset)))


def color_image(image, color):
    # zeros out rgb and preserves original transparency
    image.fill((0, 0, 0, 255), None, special_flags=pygame.BLEND_RGBA_MULT)
    # adds in new rgb values
    image.fill(color + (0,), None, pygame.BLEND_RGBA_ADD)\

    return image


tile_size = 100
starting_floor_level = 1
game_state = {'paused': False,
              'runtime': True,
              'fullscreen': True}

pygame.init()
pygame.font.init()
pygame.display.set_caption('Novorus')

# sets the size of the screen; defaults to full screen
resolution = (1920, 1080)
screen = pygame.display.set_mode(resolution)  # , pygame.FULLSCREEN)
clock = pygame.time.Clock()

camera_group = CameraGroup()
collision_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()
cursor_group = pygame.sprite.GroupSingle()
hud_group = CameraGroup()
player_bars = Bars((0, 0))
enemy_bars = Bars((0, player_bars.height))
light_group = LightSources(resolution)

# hud
cursor = Cursor(tile_size, cursor_group)
menu = Menu(hud_group)

player_health_bar = HealthBar(
    (0, player_bars.coords[1] + player_bars.height - 165),
    player_bars)

player_speed_bar = SpeedBar(
    (0, player_bars.coords[1] + player_bars.height - 115),
    player_bars)

player_attack_bar = AttackBar(
    (0, player_bars.coords[1] + player_bars.height - 65), 
    player_bars)

enemy_health_bar = HealthBar(
    (0, enemy_bars.coords[1] + enemy_bars.height - 165),
    enemy_bars)

enemy_speed_bar = SpeedBar(
    (0, enemy_bars.coords[1] + enemy_bars.height - 115),
    enemy_bars)

enemy_attack_bar = AttackBar(
    (0, enemy_bars.coords[1] + enemy_bars.height - 65),
    enemy_bars)

# player
player = Player((0, 0), (75, 75), (camera_group, player_group))
pop_up_text = PopUpText()

# levels and map
level = Level(starting_floor_level, tile_size)

while game_state['runtime']:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            game_state['runtime'] = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitboxes=False)
    pop_up_text.custom_draw(player)
    cursor_group.draw(screen)

    light_group.render_lighting(player)

    player_bars.custom_draw(player_group)
    enemy_bars.custom_draw(enemy_group)
    hud_group.draw(screen)

    # updates
    if not game_state['paused']:
        camera_group.update()

    cursor_group.update()
    hud_group.update()

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()


#
