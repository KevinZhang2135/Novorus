from constants import *
from effects import *
from sprite import Sprite

import pygame


class Chest(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.chest_closed = IMAGES['chest_closed'].copy()
        self.chest_closed = pygame.transform.scale(
            self.chest_closed, size)

        self.chest_opened = IMAGES['chest_opened'].copy()
        self.chest_opened = pygame.transform.scale(
            self.chest_opened, size)

        self.image = self.chest_closed

        self.opened = False
        self.sprite_layer = 1


    def collision(self):
        # checks if the distance of the sprites are within collision distance
        if pygame.Rect.colliderect(self.rect, self.game.player.rect) and not self.opened:
            self.image = self.chest_opened
            self.opened = True

            self.game.player.inventory.add_item(
                'baguette', random.randint(1, 3))
            
            self.game.player.inventory.add_item(
                'oak_log', random.randint(1, 3))

    def update(self):
        self.collision()


class LevelExit(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.image = IMAGES['dirt_hole'].copy()
        self.image = pygame.transform.scale(self.image, size)

        self.sprite_layer = 1

    def update(self):
        if pygame.sprite.spritecollide(self, self.game.player_group, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, self.game.player_group, False, pygame.sprite.collide_mask):
                self.game.level.floor_level += 1


class AnimatedTile(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.frame = 0

        self.animation_types = []

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 0 if len(
            self.animation_types) == 0 else 1200 / len(self.animation_types)

    def set_images(self, image_file, size):
        num_of_frames = len(
            os.listdir(f'{SPRITE_PATH}/decoration/animated/{image_file}'))

        for i in range(num_of_frames):
            image = IMAGES[f'{image_file}{i + 1}'].copy()
            image = pygame.transform.scale(image, size)

            self.animation_types.append(image)

        self.image = self.animation_types[self.frame]
        self.animation_cooldown = 0 if len(
            self.animation_types) == 0 else 1200 / len(self.animation_types)

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
        super().__init__(coords, size, game, groups)
        self.sprite_layer = 3

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
                self.game,
                self.game.camera_group)
            
            smoke.set_image(f'smoke{random.randint(1, self.smoke_frames)}')
            smoke.velocity.y = -4
            smoke.expiration_time = 500

    def update(self):
        self.animation()
        self.draw_smoke()
