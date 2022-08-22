from msilib.schema import Error
import pygame
import random
import os
import csv
from constants import *

class Level:
    def __init__(self, floor_level, tile_size):
        self.tile_size = tile_size
        self._floor_level = floor_level
        self.display_surface = pygame.display.get_surface()

        self.level_updated = False
        self.transitioning = False
        self.level_transition_rect = pygame.Rect(
            -self.display_surface.get_width(),
            0,
            self.display_surface.get_width(),
            self.display_surface.get_height())

        self.read_csv_level()

    @property
    def floor_level(self):
        return self._floor_level

    @floor_level.setter
    def floor_level(self, value):
        self._floor_level = value

        self.transitioning = True

    def read_csv_level(self):
        files = os.listdir(f'levels/{self._floor_level}')
        for path in files:
            file_extention = os.path.splitext(path)[1]
            if file_extention != '.csv':
                raise Exception(f'File "{path}" is not recognized as a csv file.')

            with open(os.path.join(f'levels/{self._floor_level}', path)) as file:
                csv_file = csv.reader(file)
                self.create_tile_group(csv_file, path)

    def clear_level(self):
        global camera_group, player_group

        for sprite in camera_group.sprites():
            if sprite not in player_group:
                sprite.kill()
                del sprite

    def create_tile_group(self, csv_file, path):
        create_tile = {'player': self.set_player_coords,
                       'wall': self.add_walls,
                       'enemies': self.add_enemies,
                       'chest': self.add_chests,
                       'static_decor': self.add_static_decor,
                       'animated_decor': self.add_animated_decor,
                       'exit': self.add_exit}

        if path[:-4] not in create_tile:
            raise Exception(f'The csv file "{path}" is invalid.')

        for row_index, row in enumerate(csv_file):
            for col_index, id in enumerate(row):
                id = int(id)
                if id != -1 and id >= 0:
                    x = col_index * self.tile_size
                    y = row_index * self.tile_size
                    create_tile[path[:-4]](id, (x, y))

                else:
                    if id < -1:
                        raise Exception(f'Unexpected value was found in csv file "{path}".')
                    
    def set_player_coords(self, id, coords):
        global player

        player.rect.center = coords

    def add_walls(self, id, coords):
        global camera_group, collision_group

        images = ['brick_top.png',
                  'brick_middle.png',
                  'brick_bottom.png',
                  'brick_pile.png',
                  'brick_side.png']

        wall = StaticTile(
            coords,
            (100, 100),
            images[id],
            (camera_group, collision_group))

    def add_enemies(self, id, coords):
        global camera_group, enemy_group, light_group

        enemies = [Ghost,
                   Mimic,
                   Sunflower]

        sprite_size = [50, 60, 30]

        enemy = enemies[id](coords, [sprite_size[id]] * 2,
                            self.floor_level, (camera_group, enemy_group))
        enemy.rect.centerx += random.randint(-25, 25)
        enemy.rect.centery += random.randint(-25, 25)

    def add_chests(self, id, coords):
        global camera_group, collision_group

        chest = Chest(
            coords,
            (60, 60),
            (camera_group, collision_group))

    def add_static_decor(self, id, coords):
        global camera_group

        sprites = [{'file': 'grass1.png',
                    'size': 30},

                   {'file': 'grass2.png',
                    'size': 30},

                   {'file': 'grass3.png',
                    'size': 30},

                   {'file': 'rock1.png',
                    'size': 50},

                   {'file': 'rock2.png',
                    'size': 40},

                   {'file': 'rock3.png',
                    'size': 50},

                   {'file': 'rock4.png',
                    'size': 50},

                   {'file': 'tree1.png',
                    'size': 120},

                   {'file': 'tree2.png',
                    'size': 120},

                   {'file': 'tree3.png',
                    'size': 120},

                   {'file': 'tree4.png',
                    'size': 30}]

        size = round(randomize(sprites[id]['size'], 0.1))
        decor = StaticTile(
            coords,
            [size] * 2,
            sprites[id]['file'],
            camera_group)

        decor.rect.centerx += random.randint(-25, 25)
        decor.rect.centery += random.randint(-25, 25)

        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

    def add_animated_decor(self, id, coords):
        global camera_group, light_group

        decor_sprites = [Torch]
        sprite_size = [50]
        size = round(randomize(sprite_size[id], 0.1))

        decor = decor_sprites[id](
            coords,
            [size] * 2,
            (camera_group, light_group))

    def add_exit(self, id, coords):
        global camera_group

        exit = LevelExit(
            coords, [round(self.tile_size * 0.8)] * 2, camera_group)

    def draw(self):
        if self.transitioning:
            pygame.draw.rect(
                self.display_surface,
                BLACK,
                self.level_transition_rect)

    def update(self):
        global player

        if self.transitioning:
            self.level_transition_rect.x += 100
            if (self.level_transition_rect.x > 0
                    and not self.level_updated):
                self.level_updated = True

                self.clear_level()
                self.read_csv_level()

                player.velocity.x = 0
                player.velocity.y = 0

            if self.level_transition_rect.x > self.display_surface.get_width():
                self.level_transition_rect.x = -self.display_surface.get_width()

                self.transitioning = False
                self.level_updated = False


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2

        self.texts = []

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def add_text(self, text, coords, size, color):
        text = Text(*load_text(text, coords, size, color))
        self.texts.append(text)

    def move_text(self, text):
        '''Moves the text vertically'''
        if text.velocity > 0:
            text.rect.y -= text.velocity
            text.velocity += text.acceleration

    def custom_draw(self, player, show_hitboxes=False):
        '''Draws the screen according to player movement'''
        self.center_target(player)
        for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.sprite_layer, sprite.rect.bottom)):
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

    def update(self):
        global player

        for sprite in self.sprites():
            if (abs(player.rect.left - sprite.rect.left) < self.half_width
                or abs(player.rect.top - sprite.rect.top) < self.half_height):
                sprite.update()


class Text:
    def __init__(self, text, rect):
        self.text = text
        self.rect = rect

        self.time = pygame.time.get_ticks()
        self.acceleration = -0.1
        self.velocity = random.randint(1250, 2000) / 1000 + 1.5


class Particle(pygame.sprite.Sprite):
    def __init__(self, coords, size, image, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = IMAGES[image]
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.time = pygame.time.get_ticks()
        self.expiration_time = randomize(1000, 0.1)

        self.sprite_layer = 3

    def movement(self):
        '''Handles movement'''
        self.rect.centery -= 1

    def expire(self):
        '''Deletes particle after its expiration time'''
        if pygame.time.get_ticks() - self.time > self.expiration_time:
            self.kill()
            del self

    def update(self):
        self.movement()
        self.expire()


class LightSources(pygame.sprite.Group):
    def __init__(self, resolution):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2
        self.resolution = resolution

        self.light_size = pygame.math.Vector2(500, 500)

        self.light = IMAGES['soft_circle.png']
        self.light = pygame.transform.scale(self.light, [int(dimension) for dimension in self.light_size])
        self.light = color_image(self.light, MELLOW_YELLOW)

        self.filter = pygame.surface.Surface(self.resolution)

        # light offset
        self.offset = pygame.math.Vector2()
        self.sprite_layer = 2

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def render_lighting(self, player):
        global level

        if level.floor_level > 1:
            self.filter.fill(DARK_GREY)

        else:
            self.filter.fill(LIGHT_GREY)
        
        self.center_target(player)
        for sprite in self.sprites():
            if (abs(player.rect.left - sprite.rect.left) < self.half_width
                or abs(player.rect.top - sprite.rect.top) < self.half_height):
                offset_pos = sprite.rect.topleft \
                            - self.offset \
                            + list(map(lambda x: x / 2, sprite.rect.size)) \
                            - self.light_size / 2
                            
                self.filter.blit(self.light, offset_pos)

        self.display_surface.blit(
            self.filter,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)


class Menu(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        menu_width = 350
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
        self.yellow_exit_text = load_text(
            'Exit',
            (self.menu_rect.centerx, self.menu_rect.bottom - self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            YELLOW)

        self.black_exit_text = load_text(
            'Exit',
            (self.menu_rect.centerx, self.menu_rect.bottom - self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            BLACK)

        self.exit_text = self.black_exit_text
    
    def draw(self):
        global game_state

        for sprite in self.sprites():
            self.display_surface.blit(sprite.image, sprite.rect.topleft)

        if game_state['paused']:
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


class MenuButton(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 100, 100

        self.menu_sprites = {}
        self.menu_sprites['menu'] = IMAGES['menu.png']
        self.menu_sprites['menu'] = pygame.transform.scale(
            self.menu_sprites['menu'], (self.width, self.height))

        self.menu_sprites['paused'] = IMAGES['paused.png']
        self.menu_sprites['paused'] = pygame.transform.scale(
            self.menu_sprites['paused'], (self.width, self.height))

        self.image = self.menu_sprites['menu']

        self.rect = self.image.get_rect(
            bottomright=[self.display_surface.get_width(),
                         self.display_surface.get_height()])

        self.pressed = False

    def pausing(self):
        global game_state

        pause_left_click = (pygame.mouse.get_pressed()[0]
                            and self.rect.collidepoint(pygame.mouse.get_pos()))

        pause_key = pygame.key.get_pressed()[pygame.K_ESCAPE]

        # checks for left click or escape_key to popup menu
        if (pause_left_click or pause_key) and not self.pressed:
            self.pressed = True
            game_state['paused'] = not game_state['paused']

        elif not (pause_left_click or pause_key) and self.pressed:
            self.pressed = False

        if game_state['paused']:
            self.image = self.menu_sprites['paused']

        else:
            self.image = self.menu_sprites['menu']

    def update(self):
        '''Handles events'''
        self.pausing()


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 60, 60
        self.bar_width = self.width * 1.7
        self.bar_height = 15

        self.image = IMAGES['heart.png']
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
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
        if ratio > 1:
            ratio = 1

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

        self.width, self.height = 60, 60
        self.bar_width = self.width * 1.7
        self.bar_height = 15

        self.image = IMAGES['lightning.png']
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
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

        self.width, self.height = 60, 60
        self.bar_width = self.width * 1.7
        self.bar_height = 15

        self.image = IMAGES['sword.png']
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
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
        self.exp_height = self.height * 0.167
        self.exp_rect = pygame.Rect(
            self.coords, (self.exp_width, self.exp_height))

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

            # draws the card of the target's health, speed, and attack
            if target and target.show_stats:
                pygame.draw.rect(self.display_surface, BROWN, self.rect)
                pygame.draw.rect(self.display_surface,
                                 DARK_BROWN, self.rect, 5)

                name_text, name_text_rect = load_text(
                    f'{target.name} lvl {target.level}',
                    (self.coords.x + self.width / 2,
                     self.coords.y + self.height * 0.15),
                    self.height * 0.125,
                    BLACK)

                self.display_surface.blit(name_text, name_text_rect)

                # blits the bar
                for sprite in self.sprites():
                    sprite.draw(target)
                    self.display_surface.blit(sprite.image, sprite.rect.topleft)

                # displays exp if the cursor is hovered over the name
                if name_text_rect.collidepoint(pygame.mouse.get_pos()):
                    if target.exp_levels:
                        text = f'exp {target.exp} / {target.exp_levels[target.level - 1]}'

                    else:
                        text = f'exp {target.exp}'

                    exp_text, exp_text_rect = load_text(
                        text,
                        self.exp_rect.center,
                        self.exp_height * 0.75,
                        BLACK)

                    self.exp_rect.width = exp_text_rect.width + 20
                    self.exp_rect.topleft = pygame.mouse.get_pos()

                    pygame.draw.rect(self.display_surface,
                                     BROWN, self.exp_rect)
                    pygame.draw.rect(self.display_surface,
                                     DARK_BROWN, self.exp_rect, 3)
                    self.display_surface.blit(exp_text, exp_text_rect)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, tile_size, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        self.tile_size = tile_size

        self.image = IMAGES['cursor.png']
        self.image = pygame.transform.scale(self.image, (100, 100))

        self.rect = self.image.get_rect(center=(0, 0))

        self.sprite_layer = 4

    def update(self):
        global player

        coords = self.offset_mouse_pos()
        coords[0] = round(coords[0] / TILE_SIZE) * TILE_SIZE
        coords[0] -= player.rect.centerx - self.display_surface.get_width() / 2

        coords[1] = round(coords[1] / TILE_SIZE) * TILE_SIZE
        coords[1] -= player.rect.centery - \
            self.display_surface.get_height() / 2

        self.rect.center = coords

    @staticmethod
    def offset_mouse_pos():
        global player

        display_surface = pygame.display.get_surface()
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += player.rect.centerx - display_surface.get_width() / 2
        mouse_pos[1] += player.rect.centery - display_surface.get_height() / 2

        return mouse_pos


class Inventory:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.items = {}

    def display(self):
        pass


class GenericNPC:
    def face_enemy(self, target):
        if self.rect.centerx < target.rect.centerx:
            self.facing = 'right'

        else:
            self.facing = 'left'

    def attack_enemy(self, target_group):
        global camera_group

        # checks if the player mask overlaps an enemy mask
        if (pygame.sprite.spritecollide(self, target_group, False)
            and pygame.sprite.spritecollide(self, target_group, False, pygame.sprite.collide_mask)):
            try:
                self.velocity.x = 0
                self.velocity.y = 0

            except AttributeError:
                pass

            distance = pygame.math.Vector2(self.rect.center)
            closest_distance = lambda enemy: distance.distance_to(enemy.rect.center)

            enemies = target_group.sprites()
            enemy = sorted(enemies, key=closest_distance)[0] # closest enemy
            self.face_enemy(enemy)

            if not self.in_combat:
                self.in_combat = True
                self.show_stats = True

                self.animation_time = pygame.time.get_ticks()
                self.cooldown = self.attack_cooldown
                self.frame = 0

            if self.in_combat:
                if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.cooldown:
                    self.attacking = True
                    self.frame = 0

                # only deal damage when animation ends
                if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                    if pygame.time.get_ticks() - self.animation_time > self.cooldown:
                        enemy.hurt(self.attack['current'], self.crit_chance['current'])
                        if enemy.health['current'] <= 0:
                            self.in_combat = False
                            self.exp += enemy.exp

        else:
            self.in_combat = False
            self.attacking = False

    def check_state(self):
        if not self.in_combat:
            self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        if self.health['current'] < 0:
            # sprite dies
            self.health['current'] = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = player.animation_cooldown

            for i in range(5):
                x_offset = round((self.rect.right - self.rect.left) / 4)
                x = random.randint(
                    self.rect.centerx - x_offset, 
                    self.rect.centerx + x_offset)

                y_offset = round((self.rect.bottom - self.rect.top) / 4)
                y = random.randint(
                    self.rect.centery - y_offset, 
                    self.rect.centery + y_offset)

                dust = Particle(
                    (x, y),
                    [randomize(self.rect.width / 2, 0.05) for i in range(2)],
                    f'dust{random.randint(1, 3)}.png',
                    camera_group)

            self.kill()
            del self

    def hurt(self, attack, crit_chance):
        text_coords = [
            random.randint(
                round((self.rect.left + self.rect.centerx) / 2),
                round((self.rect.right + self.rect.centerx) / 2)),
            self.rect.top]

        dodge = self.dodge_chance['current'] >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2
                camera_group.add_text(
                    damage, text_coords, 35, BLOOD_RED)

            else:
                camera_group.add_text(
                    damage, text_coords, 30, RED)

            self.health['current'] -= damage

        else:
            camera_group.add_text('Dodged', text_coords, 20, GOLD)

    def animation(self):
        '''Handles animation'''

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


class Player(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size
        
        self.in_combat = False
        self.attacking = False
        self.show_stats = True

        self.action = 'idle'
        self.facing = 'right'
        self.name = 'Player'

        # movement
        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_velocity = 7

        # stats
        self.exp = 0 # max exp is 9900
        self.exp_levels = [i for i in range(100, 10000, 100)]
        self.level = 1
        while self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

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

        self.crit_chance = {'current': 0.05,
                            'base': 0.05}

        self.dodge_chance = {'current': 0.01,
                             'base': 0.01}

        self.set_stats()

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'run': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/player/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'knight_{type}{i + 1}.png']
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])
        self.attack_cooldown = 1200 / len(self.animation_types['attack'])
        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1

    def set_stats(self):
        '''Scales stats according to its base and bonuses'''
        stats = {'health': self.health,
                 'speed': self.speed,
                 'attack': self.attack}

        for type in stats:
            ratio = stats[type]['current'] / stats[type]['total']

            stats[type]['total'] = round(stats[type]['base']
                                         * (1 + self.bonuses[type])
                                         * (1.05**(self.level - 1)))

            stats[type]['current'] = round(ratio * stats[type]['total'])

            self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
            if self.crit_chance['current'] > 0.5: # crit chance caps at 50%
                self.crit_chance['current'] = 0.5

            self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
            if self.dodge_chance['current'] > 0.33: # dodge chance caps at 33%
                self.dodge_chance['current'] = 0.33

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
                # movement decay when input is not received
                self.velocity *= 0.8

            # movement decay when the speed is low
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

    def leveling_up(self):
        '''Increases player level when they reach exp cap'''
        if self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

    def check_state(self):
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

    def hurt(self, attack, crit_chance):
        text_coords = [
            random.randint(
                round((self.rect.left + self.rect.centerx) / 2),
                round((self.rect.right + self.rect.centerx) / 2)),
            self.rect.top]

        dodge = self.dodge_chance['current'] >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2
                camera_group.add_text(
                    damage, text_coords, 35, ORANGE)

            else:
                camera_group.add_text(
                    damage, text_coords, 30, TANGERINE)

            self.health['current'] -= damage

        else:
            camera_group.add_text('Dodged', text_coords, 20, GOLD)

        if self.health['current'] < 0:
            # sprite dies
            self.health['current'] = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = player.animation_cooldown

    def update(self):
        '''Handles events'''
        global enemy_group

        self.movement()
        self.collision()
        self.attack_enemy(enemy_group)
        self.check_state()
        self.animation()
        self.leveling_up()


class Ghost(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = True

        self.action = 'idle'
        self.facing = random.choice(['left', 'right'])
        self.name = 'Ghost'

        # stats
        self.exp = 15
        self.exp_levels = False
        self.level = level

        self.health = {'current': round(30 * (1.1**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(10 * (1.1**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(6 * (1.1**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.crit_chance = {'current': 0.05,
                            'base': 0.05}

        self.dodge_chance = {'current': 0.1,
                             'base': 0.1}

        self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
        if self.crit_chance['current'] > 0.5:
            self.crit_chance['current'] = 0.5

        self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
        if self.dodge_chance['current'] > 0.33:
            self.dodge_chance['current'] = 0.33

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/enemies/ghost/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'ghost_{type}{i + 1}.png']
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])
        self.attack_cooldown = 1200 / len(self.animation_types['attack'])
        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1

    def update(self):
        '''Handles events'''
        global player_group

        self.attack_enemy(player_group)
        self.check_state()
        self.animation()


class Mimic(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.action = 'idle'
        self.facing = random.choice(['left', 'right'])
        self.name = 'Mimic'

        # stats
        self.exp = 50
        self.exp_levels = False
        self.level = level

        self.health = {'current': round(100 * (1.2**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(20 * (1.15**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(7 * (1.05**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.crit_chance = {'current': 0.15,
                            'base': 0.15}

        self.dodge_chance = {'current': 0,
                             'base': 0}

        self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
        if self.crit_chance['current'] > 0.5:
            self.crit_chance['current'] = 0.5

        self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
        if self.dodge_chance['current'] > 0.33:
            self.dodge_chance['current'] = 0.33

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'sprites/enemies/mimic/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'mimic_{type}{i + 1}.png']
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])
        self.attack_cooldown = 1200 / len(self.animation_types['attack'])
        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1

    def update(self):
        '''Handles events'''
        global player_group

        self.attack_enemy(player_group)
        self.check_state()
        self.animation()


class Sunflower(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.action = 'idle'
        self.facing = random.choice(['left', 'right'])
        self.name = 'Sunflower'

        # stats
        self.exp = 5
        self.exp_levels = False
        self.level = level

        self.health = {'current': round(25 * (1.05**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(7 * (1.05**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': 0}
        self.speed['total'] = self.speed['current']

        self.crit_chance = {'current': 0.05,
                            'base': 0.05}

        self.dodge_chance = {'current': 0,
                             'base': 0}

        self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
        if self.crit_chance['current'] > 0.5:
            self.crit_chance['current'] = 0.5

        self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
        if self.dodge_chance['current'] > 0.33:
            self.dodge_chance['current'] = 0.33

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'sprites/enemies/sunflower/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'sunflower_{type}{i + 1}.png']
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])
        self.attack_cooldown = 1200 / len(self.animation_types['attack'])
        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1

    def update(self):
        '''Handles events'''
        global player_group

        self.attack_enemy(player_group)
        self.check_state()
        self.animation()


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.chest_sprites = {}
        self.chest_sprites['closed'] = IMAGES['chest_closed.png']
        self.chest_sprites['closed'] = pygame.transform.scale(
            self.chest_sprites['closed'], (self.width, self.height))

        self.chest_sprites['opened'] = IMAGES['chest_opened.png']
        self.chest_sprites['opened'] = pygame.transform.scale(
            self.chest_sprites['opened'], (self.width, self.height))
        self.image = self.chest_sprites['closed']

        self.rect = self.image.get_rect(center=coords)
        self.opened = False

        self.sprite_layer = 1

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

        self.image = IMAGES['dirt_hole.png']
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.sprite_layer = 1

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

        self.image = IMAGES[image]
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.sprite_layer = 1


class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, images, groups):
        super().__init__(groups)
        self.width, self.height = size
        self.frame = 0

        self.animation_types = []
        num_of_frames = len(
            os.listdir(f'sprites/decoration/animated/{images}'))

        for i in range(num_of_frames):
            image = IMAGES[f'{images}{i + 1}.png']
            image = pygame.transform.scale(image, size)

            self.animation_types.append(image)

        self.image = self.animation_types[self.frame]
        self.rect = self.image.get_rect(center=coords)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1200 / len(self.animation_types)

        self.sprite_layer = 1

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


class Torch(AnimatedTile):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(coords, size, 'torch', groups)
        self.sprite_layer = 2
        self.rect.centerx += random.randint(-1, 1) * 25
        self.rect.centery += 25

        self.smoke_time = pygame.time.get_ticks() + random.randint(1000, 2000)
        self.smoke_cooldown = randomize(5000, 0.2)
        
        self.smoke_frames = len(
            os.listdir(f'sprites/particles/smoke'))

    def draw_smoke(self):
        if pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            self.smoke_time = pygame.time.get_ticks()
            x = self.rect.centerx
            y = random.randint(self.rect.top, self.rect.centery)

            smoke = Particle(
                (x, y),
                [randomize(20, 0.1) for i in range(2)],
                f'smoke{random.randint(1, self.smoke_frames)}.png',
                camera_group)

            smoke.expiration_time = randomize(1500, 0.1)
            
    def update(self):
        self.animation()
        self.draw_smoke()


def load_text(text, coords, text_size, color):
    '''Returns text and its rect'''
    # "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0
    font = pygame.font.Font('comicoro.ttf', round(text_size))
    # pygame.font.Font.set_bold(font, 1) # creates a bold font if the boolean is true

    text = font.render(str(text), True, color)
    text_rect = text.get_rect(center=coords)

    return text, text_rect


def randomize(value: int, offset: float):
    '''Randomizes the value with a +- deviation of the offset'''
    return random.randint(
        round(value * (1 - offset)),
        round(value * (1 + offset)))


def color_image(image, color):
    '''Recolors a surface'''
    # zeros out rgb and preserves original transparency
    image.fill((0, 0, 0, 255), None, special_flags=pygame.BLEND_RGBA_MULT)
    # adds in new rgb values
    image.fill(color + (0,), None, pygame.BLEND_RGBA_ADD)\

    return image


# pygame setup is declared in constants.py to create images

# sprite groups
camera_group = CameraGroup()
collision_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()
cursor_group = pygame.sprite.GroupSingle()
light_group = LightSources(RESOLUTION)

menu = Menu()

player_bars = Bars((0, 0))
enemy_bars = Bars((0, player_bars.height))


# hud
cursor = Cursor(TILE_SIZE, cursor_group)
menu_button = MenuButton(menu)

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

# levels and map
level = Level(STARTING_FLOOR, TILE_SIZE)

while game_state['runtime']:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            game_state['runtime'] = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitboxes=False)
    cursor_group.draw(screen)
    light_group.render_lighting(player)

    player_bars.custom_draw(player_group)
    enemy_bars.custom_draw(enemy_group)

    menu.draw()
    level.draw()

    # updates
    if not game_state['paused'] and not level.transitioning:
        camera_group.update()

    cursor_group.update()
    menu.update()
    level.update()

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()


#
