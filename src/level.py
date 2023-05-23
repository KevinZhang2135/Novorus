from constants import *
from entities import *

import pygame
import os
import csv
import random


class Level:
    def __init__(self, floor_level, tile_size, game):
        global player

        self.game = game

        self.size = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, 0, 0)

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

        text = COMICORO[50].render(f'Floor {self.floor_level}', True, BLACK)
        text_rect = text.get_rect(
            center=(self.display_surface.get_width() / 2,
                    self.display_surface.get_height() - 50))

        self.floor_level_text = [text, text_rect]
        self.read_csv_level()
        self.update_lighting()

    @property
    def floor_level(self):
        return self._floor_level

    @floor_level.setter
    def floor_level(self, value):
        self._floor_level = value
        self.transitioning = True

    def transition_level(self):
        if self.transitioning:
            self.level_transition_rect.x += 75
            if (self.level_transition_rect.x > 0
                    and not self.level_updated):
                self.level_updated = True

                self.clear_level()
                self.read_csv_level()
                self.update_lighting()

                text = COMICORO[50].render(
                    f'Floor {self.floor_level}', True, BLACK)

                self.floor_level_text[0] = text

                self.game.player.velocity.x = 0
                self.game.player.velocity.y = 0

            if self.level_transition_rect.x > self.display_surface.get_width():
                self.level_transition_rect.x = -self.display_surface.get_width()

                self.transitioning = False
                self.level_updated = False

    def read_csv_level(self):
        files = os.listdir(f'{LEVEL_PATH}/{self._floor_level}')

        i = 0
        for path in files:
            file_extention = os.path.splitext(path)[1]
            if file_extention != '.csv':
                raise Exception(
                    f'File "{path}" is not recognized as a csv file.')

            with open(os.path.join(f'{LEVEL_PATH}/{self._floor_level}', path)) as file:
                csv_file = list(csv.reader(file))
                self.create_tile_group(csv_file, path)
                if not i:  # determines the dimensions of the first csv_file
                    self.size.x = len(list(csv_file)[0]) * self.tile_size
                    self.size.y = len(list(csv_file)) * self.tile_size

                    self.rect = pygame.Rect(0, 0, *self.size)
                    i += 1

    def clear_level(self):
        for sprite in self.game.camera_group.sprites():
            if sprite not in self.game.player_group:
                sprite.kill()
                del sprite

    def update_lighting(self):
        if self.floor_level > 1:
            self.game.light_group.color = MIDNIGHT

    def create_tile_group(self, csv_file, path):
        create_tile = {'player': self.set_player_coords,
                       'terrain': self.add_terrain,
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
                        raise Exception(
                            f'Unexpected value was found in csv file "{path}".')

    def set_player_coords(self, id, coords):
        self.game.player.rect.center = coords
        self.game.player.coords = self.game.player.rect.center

    def add_terrain(self, id, coords):
        sprites = ('path1',
                   'path2',
                   'path3',
                   'path4',
                   'path5',
                   'path6',
                   'path7',
                   'path8',
                   'path9',
                   'path10',
                   'grassy1',
                   'grassy2',
                   'path11',
                   'path12',
                   'path13',
                   'path14',
                   'path15',
                   'path16',
                   'path17',
                   'path18',
                   'path19',
                   'path20',
                   'path21',
                   'path22',
                   'path23',
                   'path24',
                   'path25',
                   'path26',
                   'path27',
                   'path28',
                   'path29',
                   'path30',
                   'path31',
                   'grassy3',
                   'grassy4',
                   'grassy5',
                   'grassy6',
                   )

        size = (100,) * 2
        terrain_tile = StaticTile(
            coords,
            size,
            sprites[id],
            self.game.camera_group)

        terrain_tile.sprite_layer = -1

    def add_walls(self, id, coords):
        images = ('brick_top',
                  'brick_middle',
                  'brick_bottom',
                  'brick_pile',
                  'brick_side')

        wall = StaticTile(
            coords,
            (100, 100),
            images[id],
            (self.game.camera_group, self.game.collision_group))

    def add_enemies(self, id, coords):
        enemies = (Ghost,
                   Mimic,
                   Sunflower)

        sprite_size = (50, 60, 30)

        enemy = enemies[id](coords, [sprite_size[id]] * 2,
                            self.floor_level, self.game, (self.game.camera_group, self.game.enemy_group))

        enemy.rect.centerx += random.randint(-25, 25)
        enemy.rect.centery += random.randint(-25, 25)

    def add_chests(self, id, coords):
        chest = Chest(
            coords,
            (60, 60),
            self.game,
            (self.game.camera_group, self.game.collision_group))

    def add_static_decor(self, id, coords):
        sprites = ({'file': 'grass1',
                    'size': 30},

                   {'file': 'grass2',
                    'size': 30},

                   {'file': 'grass3',
                    'size': 30},

                   {'file': 'rock1',
                    'size': 50},

                   {'file': 'rock2',
                    'size': 40},

                   {'file': 'rock3',
                    'size': 50},

                   {'file': 'rock4',
                    'size': 50},

                   {'file': 'tree1',
                    'size': 120},

                   {'file': 'tree2',
                    'size': 120},

                   {'file': 'tree3',
                    'size': 120},

                   {'file': 'tree4',
                    'size': 30})

        size = round(randomize(sprites[id]['size'], 0.1))
        decor = StaticTile(
            coords,
            [size] * 2,
            sprites[id]['file'],
            self.game.camera_group)

        decor.rect.centerx += random.randint(-25, 25)
        decor.rect.centery += random.randint(-25, 25)

        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

    def add_animated_decor(self, id, coords):
        decor_sprites = (Torch,)
        sprite_size = (50,)
        size = round(randomize(sprite_size[id], 0.1))

        decor = decor_sprites[id](
            coords,
            [size] * 2,
            self.game,
            (self.game.camera_group, self.game.light_group))

        decor.sprite_layer = 2

    def add_exit(self, id, coords):
        exit = LevelExit(
            coords,
            [round(self.tile_size * 0.8)] * 2,
            self.game,
            self.game.camera_group
        )

    def draw(self):
        self.display_surface.blit(*self.floor_level_text)

        if self.transitioning:
            pygame.draw.rect(
                self.display_surface,
                BLACK,
                self.level_transition_rect)

    def update(self):
        """Handles events"""
        self.transition_level()


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(groups)
        self.game = game
        self.width, self.height = size

        self.chest_sprites = {}
        self.chest_sprites['closed'] = IMAGES['chest_closed'].copy()
        self.chest_sprites['closed'] = pygame.transform.scale(
            self.chest_sprites['closed'], (self.width, self.height))

        self.chest_sprites['opened'] = IMAGES['chest_opened'].copy()
        self.chest_sprites['opened'] = pygame.transform.scale(
            self.chest_sprites['opened'], (self.width, self.height))
        self.image = self.chest_sprites['closed']

        self.rect = self.image.get_rect(center=coords)
        self.opened = False

        self.sprite_layer = 1

    def collision(self):
        # checks if the distance of the sprites are within collision distance
        if pygame.Rect.colliderect(self.rect, self.game.player.rect) and not self.opened:
            self.image = self.chest_sprites['opened']
            self.opened = True

            self.game.player.inventory.add_item(
                'baguette', random.randint(1, 3))
            self.game.player.inventory.add_item(
                'oak_log', random.randint(1, 3))

    def update(self):
        self.collision()


class LevelExit(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(groups)
        self.game = game
        self.width, self.height = size

        self.image = IMAGES['dirt_hole'].copy()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.sprite_layer = 1

    def update(self):
        if pygame.sprite.spritecollide(self, self.game.player_group, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, self.game.player_group, False, pygame.sprite.collide_mask):
                self.game.level.floor_level += 1


class StaticTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, image: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = IMAGES[image].copy()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.sprite_layer = 1


class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, images, game, groups):
        super().__init__(groups)
        self.game = game
        self.width, self.height = size
        self.frame = 0

        self.animation_types = []
        num_of_frames = len(
            os.listdir(f'{SPRITE_PATH}/decoration/animated/{images}'))

        for i in range(num_of_frames):
            image = IMAGES[f'{images}{i + 1}'].copy()
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
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, 'torch', game, groups)
        self.sprite_layer = 2
        self.rect.centerx += random.randint(-1, 1) * 25
        self.rect.centery += 25

        self.smoke_time = pygame.time.get_ticks() + random.randint(1000, 2000)
        self.smoke_cooldown = randomize(4000, 0.2)

        self.smoke_frames = len(
            os.listdir(f'{SPRITE_PATH}/particles/smoke'))

        self.light_size = pygame.math.Vector2(500, 500)

        self.light = IMAGES['soft_circle'].copy()
        self.light = pygame.transform.scale(
            self.light, [int(dimension) for dimension in self.light_size])
        self.light = color_image(self.light, MELLOW_YELLOW, transparency=100)

    def draw_smoke(self):
        if pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            self.smoke_time = pygame.time.get_ticks()
            self.smoke_cooldown = randomize(4000, 0.2)

            smoke = Particle(
                self.rect.center,
                [randomize(25, 0.1) for i in range(2)],
                f'smoke{random.randint(1, self.smoke_frames)}',
                self.game.camera_group)

            smoke.velocity.y = -4
            smoke.expiration_time = 500

    def update(self):
        self.animation()
        self.draw_smoke()
