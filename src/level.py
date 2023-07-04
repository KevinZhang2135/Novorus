from constants import *
from tiles import *

from enemies import *
from entity import *
from sprite import Sprite

import pygame
import os
import csv
import random


class Level:
    def __init__(self, floor_level: int, game):
        self.game = game

        self.size = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.floor_level = floor_level
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

    def transition_level(self):
        # draws rectangle to cover screen as level transitions
        if self.transitioning:
            self.level_transition_rect.x += 75
            if (self.level_transition_rect.x > 0
                    and not self.level_updated):

                self.level_updated = True
                self.floor_level += 1

                # updates level map
                self.clear_level()
                self.read_csv_level()
                self.update_lighting()

                # updates floor level text
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
        files = os.listdir(f'{LEVEL_PATH}/{self.floor_level}')
        row = 0

        # reads csv files in folder
        for path in files:
            # checks if file is not csv
            file_extention = os.path.splitext(path)[1]
            if file_extention != '.csv':
                raise Exception(
                    f'File "{path}" is not recognized as a csv file.'
                )

            # reads csv
            with open(os.path.join(f'{LEVEL_PATH}/{self.floor_level}', path)) as file:
                csv_file = list(csv.reader(file))
                self.create_tile_group(csv_file, path)

                if not row:  # determines the dimensions of the first csv_file
                    self.size.x = len(list(csv_file)[0]) * TILE_SIZE
                    self.size.y = len(list(csv_file)) * TILE_SIZE

                    self.rect = pygame.Rect(0, 0, *self.size)
                    row += 1

    def clear_level(self):
        for sprite in self.game.camera_group.sprites():
            if sprite not in self.game.player_group:
                sprite.kill()
                del sprite

    def create_tile_group(self, csv_file, path: str):
        create_tile = {
            'player': self.set_player_coords,
            'terrain': self.add_terrain,
            'terrain_overlay': self.add_terrain_overlay,
            'walls': self.add_walls,
            'enemies': self.add_enemies,
            'chests': self.add_chests,
            'static_decor': self.add_static_decor,
            'animated_decor': self.add_animated_decor,
            'totems': self.add_totems
        }

        if path[:-4] not in create_tile:
            raise Exception(f'The csv file "{path}" is invalid.')

        # creates sprite according to csv data of ids
        for row_index, row in enumerate(csv_file):
            for col_index, id in enumerate(row):
                id = int(id)

                # id -1 is empty
                if id != -1 and id >= 0:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
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
        sprites = [f'path{i}' for i in range(1, 32)] \
            + [f'grassy{i}' for i in range(1, 12)] \

        size = (TILE_SIZE,) * 2
        terrain_tile = Sprite(
            coords,
            size,
            self.game,
            self.game.camera_group
        )

        terrain_tile.set_image(sprites[id])

    def add_terrain_overlay(self, id: int, coords: list):
        sprites = [f'bricks{i}' for i in range(1, 5)] \
            + [f'ditch{i}' for i in range(1, 5)] \
            + [f'grassy_patch{i}' for i in range(1, 9)]

        size = (TILE_SIZE,) * 2
        terrain_tile = Sprite(
            coords,
            size,
            self.game,
            self.game.camera_group
        )

        terrain_tile.set_image(sprites[id])
        terrain_tile.sprite_layer = 2

    def add_walls(self, id: int, coords: list):
        sprites = (
            'brick_top',
            'brick_middle',
            'brick_bottom',
            'brick_pile',
            'brick_side'
        )

        size = (TILE_SIZE,) * 2
        wall = Sprite(
            coords,
            size,
            self.game,
            (self.game.camera_group, self.game.collision_group)
        )

        wall.set_image(sprites[id])
        wall.sprite_layer = 3

        match id:
            case 0:
                wall.set_hitbox(1, 0.8, offsety=0.1)

            case 3:
                wall.set_hitbox(0.7, 0.4, offsety=0.05)

            case 4:
                wall.set_hitbox(1, 0.8, offsety=0.1)

            case _:
                pass

    def add_enemies(self, id: int, coords: list):
        enemies = (
            Ghost,
            Mimic,
            Sunflower,
            Acorn
        )

        size = (50, 80, 90, 60)
        enemy = enemies[id](
            coords,
            [size[id]] * 2,
            self.game,
            (self.game.camera_group, self.game.enemy_group)
        )

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
            # flower1
            case 0:
                size = (round(randomize(TILE_SIZE * 0.9, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('flower1')
                decor.set_hitbox(0.25, 0.4)
                decor.sprite_layer = 3

            # bush1
            case 1:
                size = (round(randomize(TILE_SIZE * 0.8, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('bush1')
                decor.set_hitbox(0.6, 0.5)
                decor.sprite_layer = 3

            # bush2
            case 2:
                size = (round(randomize(TILE_SIZE * 0.8, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('bush2')
                decor.set_hitbox(0.6, 0.3)
                decor.sprite_layer = 3

            # rock1
            case 3:
                size = (round(randomize(TILE_SIZE * 0.8, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('rock1')
                decor.set_hitbox(0.4, 0.3, offsety=0.1)
                decor.sprite_layer = 3

            # rock2
            case 4:
                size = (round(randomize(TILE_SIZE * 0.7, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('rock2')
                decor.set_hitbox(0.4, 0.4, offsety=0.1)
                decor.sprite_layer = 3

            # rock3
            case 5:
                size = (round(randomize(TILE_SIZE * 0.6, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('rock3')
                decor.set_hitbox(0.4, 0.4, offsety=0.1)
                decor.sprite_layer = 3

            # rock4
            case 6:
                size = (round(randomize(TILE_SIZE * 0.8, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-25, 25)
                coords[1] += random.randint(-25, 25)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('rock4')
                decor.set_hitbox(0.4, 0.4, offsety=0.1)
                decor.sprite_layer = 3

            # oak tree
            case 7:
                size = (round(randomize(TILE_SIZE * 2, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-50, 50)
                coords[1] += random.randint(-50, 50)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('oak_tree')
                decor.set_hitbox(0.4, 0.6)
                decor.sprite_layer = 3

            # pine tree
            case 8:
                size = (round(randomize(TILE_SIZE * 2, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-50, 50)
                coords[1] += random.randint(-50, 50)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('pine_tree')
                decor.set_hitbox(0.3, 0.6)
                decor.sprite_layer = 3

            # sakura tree
            case 9:
                size = (round(randomize(TILE_SIZE * 2, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-50, 50)
                coords[1] += random.randint(-50, 50)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('sakura_tree')
                decor.set_hitbox(0.3, 0.6)
                decor.sprite_layer = 3

            # dead tree
            case 10:
                size = (round(randomize(TILE_SIZE * 1.8, 0.1)), ) * 2

                # randomly offsets
                coords[0] += random.randint(-50, 50)
                coords[1] += random.randint(-50, 50)

                decor = Sprite(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

                decor.set_image('dead_tree')
                decor.set_hitbox(0.3, 0.65)
                decor.sprite_layer = 3

        # randomly flips vertically
        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

    def add_animated_decor(self, id: int, coords: list):
        match id:
            # torch
            case 0:
                size = (round(randomize(TILE_SIZE, 0.1)), ) * 2
                decor = Torch(
                    coords,
                    size,
                    self.game,
                    self.game.camera_group
                )

    def add_totems(self, id: int, coords: list):
        totem = Totem(
            coords,
            (TILE_SIZE * 1.75,) * 2,
            self.game,
            (self.game.camera_group, self.game.enemy_group, self.game.totem_group)
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
