from constants import *
from entity import *
from tiles import *
from enemies import *
from sprite import Sprite

import pygame
import os
import csv
import random


class Level:
    def __init__(self, floor_level: int, tile_size: int, game):
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
            self.display_surface.get_height()
        )

        text = COMICORO[50].render(f'Floor {self.floor_level}', True, BLACK)
        text_rect = text.get_rect(
            center=(
                self.display_surface.get_width() / 2,
                self.display_surface.get_height() - 50
            )
        )

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
        # draws rectangle to cover screen as level transitions
        if self.transitioning:
            self.level_transition_rect.x += 75
            if (self.level_transition_rect.x > 0
                    and not self.level_updated):
                self.level_updated = True

                # updates level map
                self.clear_level()
                self.read_csv_level()
                self.update_lighting()

                text = COMICORO[50].render(
                    f'Floor {self.floor_level}',
                    True,
                    BLACK
                )

                self.floor_level_text[0] = text

                self.game.player.velocity.x = 0
                self.game.player.velocity.y = 0

            # finishes updating
            if self.level_transition_rect.x > self.display_surface.get_width():
                self.level_transition_rect.x = -self.display_surface.get_width()

                self.transitioning = False
                self.level_updated = False

    def read_csv_level(self):
        files = os.listdir(f'{LEVEL_PATH}/{self._floor_level}')

        i = 0
        # reads csv files in folder
        for path in files:
            # checks if file is not csv
            file_extention = os.path.splitext(path)[1]
            if file_extention != '.csv':
                raise Exception(
                    f'File "{path}" is not recognized as a csv file.'
                )

            # reads csv
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

    def create_tile_group(self, csv_file, path: str):
        create_tile = {
            'player': self.set_player_coords,
            'terrain': self.add_terrain,
            'wall': self.add_walls,
            'enemies': self.add_enemies,
            'chest': self.add_chests,
            'static_decor': self.add_static_decor,
            'animated_decor': self.add_animated_decor,
            'exit': self.add_exit
        }

        if path[:-4] not in create_tile:
            raise Exception(f'The csv file "{path}" is invalid.')

        # creates sprite according to csv data of ids
        for row_index, row in enumerate(csv_file):
            for col_index, id in enumerate(row):
                id = int(id)

                # id -1 is empty
                if id != -1 and id >= 0:
                    x = col_index * self.tile_size
                    y = row_index * self.tile_size
                    create_tile[path[:-4]](id, [x, y])

                else:
                    # corrupted csv
                    if id < -1:
                        raise Exception(
                            f'Unexpected value was found in csv file "{path}".'
                        )

    def set_player_coords(self, id: int, coords: list):
        self.game.player.set_coords(*coords)

    def add_terrain(self, id: int, coords: list):
        sprites = [f'path{i + 1}' for i in range(0, 10)] \
            + [f'grassy{i + 1}' for i in range(0, 2)] \
            + [f'path{i + 1}' for i in range(10, 31)] \
            + [f'grassy{i + 1}' for i in range(2, 6)]

        size = (100,) * 2
        terrain_tile = Sprite(
            coords,
            size,
            self.game,
            self.game.camera_group
        )

        terrain_tile.set_image(sprites[id], size)

    def add_walls(self, id: int, coords: list):
        sprites = (
            'brick_top',
            'brick_middle',
            'brick_bottom',
            'brick_pile',
            'brick_side'
        )

        size = (100,) * 2
        terrain_tile = Sprite(
            coords,
            size,
            self.game,
            (self.game.camera_group, self.game.collision_group)
        )

        terrain_tile.set_image(sprites[id], size)
        terrain_tile.sprite_layer = 1

    def add_enemies(self, id: int, coords: list):
        enemies = (
            Ghost,
            Mimic,
            Sunflower
        )

        size = (50, 80, 30)
        enemy = enemies[id](coords, [size[id]] * 2, self.game,
                            (self.game.camera_group, self.game.enemy_group))

        enemy.set_coords(
            enemy.coords.x + random.randint(-25, 25),
            enemy.coords.y + random.randint(-25, 25)
        )

    def add_chests(self, id: int, coords: list):
        size = (80, ) * 2
        chest = Chest(
            coords,
            size,
            self.game,
            (self.game.camera_group, self.game.collision_group)
        )

    def add_static_decor(self, id: int, coords: list):
        match id:
            # grass1
            case 0:
                size = (round(randomize(30, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('grass1', size)

            # grass2
            case 1:
                size = (round(randomize(30, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('grass2', size)

            # bush1
            case 2:
                size = (round(randomize(80, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('bush1', size)
                decor.set_hitbox(0.7, 0.55)

            # rock1
            case 3:
                size = (round(randomize(50, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('rock1', size)
                decor.set_hitbox(0.4, 0.3, offsety=decor.rect.height / 10)

            # rock2
            case 4:
                size = (round(randomize(40, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('rock2', size)
                decor.set_hitbox(0.4, 0.4, offsety=decor.rect.height / 10)

            # rock3
            case 5:
                size = (round(randomize(30, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('rock3', size)
                decor.set_hitbox(0.4, 0.4, offsety=decor.rect.height / 10)

            # rock4
            case 6:
                size = (round(randomize(40, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('rock4', size)
                decor.set_hitbox(0.4, 0.4, offsety=decor.rect.height / 10)

            # tree1
            case 7:
                size = (round(randomize(180, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-10, 10)
                coords[1] += random.randint(-10, 10)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('oak_tree', size)
                decor.set_hitbox(0.6, 0.6)

            # tree2
            case 8:
                size = (round(randomize(190, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-10, 10)
                coords[1] += random.randint(-10, 10)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('pine_tree', size)
                decor.set_hitbox(0.6, 0.6)

            # tree3
            case 9:
                size = (round(randomize(160, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('sakura_tree', size)
                decor.set_hitbox(0.6, 0.6)

            # tree4
            case 10:
                size = (round(randomize(150, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group)

                decor.set_image('dead_tree', size)
                decor.set_hitbox(0.6, 0.6)

        decor.sprite_layer = 1

        # randomly flips vertically
        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

    def add_animated_decor(self, id: int, coords: list):
        match id:
            # torch
            case 0:
                size = (round(randomize(50, 0.1)), ) * 2
                decor = Torch(
                    coords,
                    size,
                    self.game,
                    (self.game.camera_group, self.game.light_group)
                )

                decor.set_images('torch', size)
                decor.sprite_layer = 2

    def add_exit(self, id: int, coords: list):
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
                self.level_transition_rect
            )

    def update(self):
        """Handles events"""
        self.transition_level()
