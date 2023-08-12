from constants import *
from color import Color
from tiles import *

from enemies import *
from entity import *
from sprite import Sprite

import pygame
import csv


class Level:
    def __init__(self, floor_level: int, game):
        self.game = game

        self.size = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.floor_level = floor_level
        self.screen = pygame.display.get_surface()

        self.level_updated = False
        self.transitioning = False
        self.level_transition_rect = pygame.Rect(
            -self.screen.get_width(),
            0,
            self.screen.get_width(),
            self.screen.get_height()
        )

        # layers
        self.grass_layer = None
        self.terrain_layer = None
        self.terrain_overlay_layer = None

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

                self.game.player.velocity.x = 0
                self.game.player.velocity.y = 0

            # finishes updating
            if self.level_transition_rect.x > self.screen.get_width():
                self.level_transition_rect.x = -self.screen.get_width()

                self.transitioning = False
                self.level_updated = False

    def read_csv_level(self):
        files = os.listdir(f'{LEVEL_PATH}/{self.floor_level}')

        # reads csv files in folder
        for row, path in enumerate(files):
            # checks if file is not csv
            file_extention = os.path.splitext(path)[1]
            if file_extention != '.csv':
                raise Exception(
                    f'File "{path}" is not recognized as a csv file.'
                )

            # reads csv
            with open(os.path.join(f'{LEVEL_PATH}/{self.floor_level}', path)) as file:
                csv_file = tuple(csv.reader(file))
                if not row:  # determines the dimensions of the first csv_file
                    self.size.x = len(csv_file[0]) * TILE_SIZE
                    self.size.y = len(csv_file) * TILE_SIZE
                    self.rect = pygame.Rect(0, 0, *self.size)

                    # initializes layers
                    self.grass_layer = pygame.Surface(
                        self.size, pygame.SRCALPHA)
                    self.terrain_layer = pygame.Surface(
                        self.size, pygame.SRCALPHA)
                    self.terrain_overlay_layer = pygame.Surface(
                        self.size, pygame.SRCALPHA)

                self.create_tile_group(csv_file, path)

        # draws grass
        self.add_grass()

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
            'instructions': self.add_instructions,
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

    def add_grass(self):
        '''Places a lot of grass'''
        num_grass = (self.size.x * self.size.y) // TILE_SIZE**2 * 2
        grass_size = (TILE_SIZE * 2,) * 2

        # draws grass onto surface
        for i in range(int(num_grass)):
            filename = f'grass{random.randint(1, 7)}'
            coords = (
                random.randint(-HALF_TILE_SIZE, self.size.x + HALF_TILE_SIZE),
                random.randint(-HALF_TILE_SIZE, self.size.y + HALF_TILE_SIZE)
            )

            grass = pygame.transform.scale(
                IMAGES[filename],
                grass_size
            )

            self.grass_layer.blit(grass, coords)

    def add_terrain(self, id: int, coords: list):
        sprites = [f'path{i}' for i in range(1, 32)]

        terrain_size = (TILE_SIZE,) * 2
        terrain = pygame.transform.scale(
            IMAGES[sprites[id]],
            terrain_size
        )

        self.terrain_layer.blit(terrain, coords)

    def add_terrain_overlay(self, id: int, coords: list):
        sprites = [f'bricks{i}' for i in range(1, 5)] \
            + [f'ditch{i}' for i in range(1, 5)] \
            + [f'grassy_patch{i}' for i in range(1, 9)]

        overlay_size = (TILE_SIZE,) * 2
        overlay = pygame.transform.scale(
            IMAGES[sprites[id]],
            overlay_size
        )

        self.terrain_overlay_layer.blit(overlay, coords)

    def add_instructions(self, id: int, coords: list):
        sprites = ('dash_path', 'inventory_path', 'move_path', 'slash_path')

        size = (TILE_SIZE,) * 2
        terrain_tile = Sprite(
            coords,
            size,
            self.game,
            self.game.camera_group
        )

        terrain_tile.set_animation(sprites[id])

    def add_walls(self, id: int, coords: list):
        size = (TILE_SIZE,) * 2
        wall = Sprite(
            coords,
            size,
            self.game,
            (self.game.camera_group, self.game.collision_group)
        )

        wall.sprite_layer = 3
        wall.draw_shadow = True

        match id:
            case 0:
                wall.set_animation('brick_top')
                wall.set_hitbox(1, 0.8, offsety=0.1)

            case 1:
                wall.set_animation('brick_middle')

            case 2:
                wall.set_animation('brick_bottom')

            case 3:
                wall.set_animation('brick_pile')
                wall.set_hitbox(0.7, 0.4, offsety=0.05)

            case 4:
                wall.set_animation('brick_side')
                wall.set_hitbox(1, 0.8, offsety=0.1)

    def add_enemies(self, id: int, coords: list):
        match id:
            case 0:
                enemy = Ghost(
                    coords,
                    (TILE_SIZE * 0.7,) * 2,
                    self.game,
                    (self.game.camera_group, self.game.enemy_group)
                )

            case 1:
                enemy = Mimic(
                    coords,
                    (TILE_SIZE * 0.8,) * 2,
                    self.game,
                    (self.game.camera_group, self.game.enemy_group)
                )

            case 2:
                enemy = Sunflower(
                    coords,
                    (TILE_SIZE * 0.9,) * 2,
                    self.game,
                    (self.game.camera_group, self.game.enemy_group)
                )

            case 3:
                enemy = Acorn(
                    coords,
                    (TILE_SIZE * 0.6,) * 2,
                    self.game,
                    (self.game.camera_group, self.game.enemy_group)
                )

            case 4:
                enemy = Newtshroom(
                    coords,
                    (TILE_SIZE * 0.8,) * 2,
                    self.game,
                    (self.game.camera_group, self.game.enemy_group)
                )

        enemy.set_coords(
            enemy.coords.x + random.randint(-25, 25),
            enemy.coords.y + random.randint(-25, 25)
        )

    def add_chests(self, id: int, coords: list):
        size = (TILE_SIZE * 0.9,) * 2
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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('flower1')
                decor.set_hitbox(0.25, 0.3)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('bush1')
                decor.set_hitbox(0.6, 0.5)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('bush2')
                decor.set_hitbox(0.6, 0.3)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('rock1')
                decor.set_hitbox(0.4, 0.3, offsety=0.1)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('rock2')
                decor.set_hitbox(0.4, 0.4, offsety=0.1)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('rock3')
                decor.set_hitbox(0.4, 0.4, offsety=0.1)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('rock4')
                decor.set_hitbox(0.4, 0.4, offsety=0.1)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('oak_tree')
                decor.set_hitbox(0.4, 0.6)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('pine_tree')
                decor.set_hitbox(0.3, 0.6)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('sakura_tree')
                decor.set_hitbox(0.3, 0.6)

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

                decor.sprite_layer = 3
                decor.draw_shadow = True

                decor.set_animation('dead_tree')
                decor.set_hitbox(0.3, 0.65)

        # randomly flips vertically
        if random.randint(0, 1):
            decor.facing = 'left'
            decor.animation()

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
        match id:
            case 0:
                totem = Totem1(
                    coords,
                    (TILE_SIZE,) * 2,
                    self.game,
                    (self.game.camera_group,
                     self.game.enemy_group, self.game.totem_group)
                )

            case 1:
                totem = Totem2(
                    coords,
                    (TILE_SIZE,) * 2,
                    self.game,
                    (self.game.camera_group,
                     self.game.enemy_group, self.game.totem_group)
                )

    def draw(self):
        if self.transitioning:
            pygame.draw.rect(
                self.screen,
                Color.BLACK,
                self.level_transition_rect
            )

    def update(self):
        """Handles events"""
        self.transition_level()
