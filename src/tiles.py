from constants import *
from lighting import *
from particles import *
from sprite import Sprite
from entity import Entity

import pygame


class Chest(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # hitbox
        self.hitbox = self.rect.scale_by(0.55, 0.45)

        # sprites
        self.chest_closed = IMAGES['chest_closed'].copy()
        self.chest_closed = pygame.transform.scale(
            self.chest_closed,
            size
        )

        self.chest_opened = IMAGES['chest_opened'].copy()
        self.chest_opened = pygame.transform.scale(
            self.chest_opened,
            size
        )

        self.image = self.chest_closed

        self.opened = False
        self.sprite_layer = 3

    def collision(self):
        # checks if the distance of the sprites are within collision distance
        if pygame.Rect.colliderect(self.rect, self.game.player.hitbox) and not self.opened:
            self.image = self.chest_opened
            self.opened = True

            self.game.player.inventory.add_item(
                'baguette',
                random.randint(1, 3)
            )

            self.game.player.inventory.add_item(
                'oak_log',
                random.randint(1, 3)
            )

    def update(self):
        self.collision()


class LevelExit(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.image = IMAGES['dirt_hole'].copy()
        self.image = pygame.transform.scale(self.image, size)

        self.sprite_layer = 3

    def update(self):
        if pygame.sprite.spritecollide(self, self.game.player_group, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, self.game.player_group, False, pygame.sprite.collide_mask):
                self.game.level.floor_level += 1


class AnimatedTile(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

    def update(self):
        self.animation()


class Torch(AnimatedTile):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # hitbox
        self.set_hitbox(0.15, 0.3)

        # animation
        self.set_animation('decoration/animated/torch')
        self.animation_cooldown = 600 / len(self.animation_types)
        self.cooldown = self.animation_cooldown

        self.sprite_layer = 4

        # smoke
        self.smoke_time = pygame.time.get_ticks() + random.randint(1000, 2000)
        self.smoke_cooldown = randomize(4000, 0.2)

        self.smoke_frames = len(
            os.listdir(f'{SPRITE_PATH}/particles/smoke')
        )

        # light effects
        self.light_size = pygame.math.Vector2(500, 500)

        self.light = IMAGES['soft_circle'].copy()
        self.light = pygame.transform.scale(
            self.light, 
            [int(dimension) for dimension in self.light_size]
        )

        self.light = color_image(self.light, MELLOW_YELLOW, transparency=100)

    def draw_smoke(self):
        "Creates smoke every interval"
        if pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            self.smoke_time = pygame.time.get_ticks()
            self.smoke_cooldown = randomize(4000, 0.2)

            smoke = Particle(
                self.rect.center,
                [randomize(25, 0.1) for i in range(2)],
                self.game,
                self.game.camera_group
            )

            smoke.set_image(f'smoke{random.randint(1, self.smoke_frames)}')
            smoke.velocity.y = -4
            smoke.expiration_time = 500

    def update(self):
        self.animation()
        self.draw_smoke()
