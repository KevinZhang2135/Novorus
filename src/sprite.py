from constants import *
from shadow import Shadow

import pygame
from copy import deepcopy


class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(groups)
        self.game = game

        self.coords = pygame.math.Vector2(*coords)
        self.size = pygame.math.Vector2(*size)

        # images and rects
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center=coords)

        self.hitbox = pygame.Rect(self.rect)
        self.hitbox_offset = pygame.math.Vector2()

        # render
        self.facing = 'right'
        self.sprite_layer = 0

        # animation
        self.frame = 0
        self.loop_frames = True

        self.animation_frames = {
            'left': [],
            'right': []
        }

        # animation cooldowns
        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 0

        # masks
        self.rect_mask = pygame.mask.Mask(self.hitbox.size)
        self.rect_mask.fill()

        # shadows
        self.draw_shadow = False
        self.shadow = None
        self.shadow_frames = deepcopy(self.animation_frames)

    def get_images(self, filepath: str, isFolder=False, flipped=False):
        images = []
        shadows = []

        if isFolder:
            # sorts filenames by length and then alphabetically
            filepaths = os.listdir(f'{SPRITE_PATH}/{filepath}')
            filepaths.sort(key=lambda filename: (len(filename), filename))

            for path in filepaths:
                filename = path[:-4].split('/')[-1]
                image = IMAGES[filename].copy()
                image = pygame.transform.scale(
                    image,
                    self.size
                )

                if flipped:
                    # flips image over y-axis
                    image = pygame.transform.flip(image, True, False)

                # creates image and shadow
                images.append(image)
                if self.draw_shadow:
                    shadows.append(Shadow((0, 0, 0, 50), image))

        else:
            filename = filepath.split('/')[-1]
            image = IMAGES[filename].copy()
            image = pygame.transform.scale(image, self.size)

            if flipped:
                # flips image over y-axis
                image = pygame.transform.flip(image, True, False)

            images.append(image)
            if self.draw_shadow:
                shadows.append(Shadow((0, 0, 0, 50), image))

        return images, shadows

    def set_animation(self, filepath: str, isFolder=False):
        for facing in self.animation_frames:
            path = f'{SPRITE_PATH}/{filepath}'

            images = self.get_images(
                path,
                isFolder=isFolder,
                flipped=(facing == 'left')
            )

            self.animation_frames[facing] = images[0]
            if self.draw_shadow:
                self.shadow_frames[facing] = images[1]

        # sets image
        self.image = self.animation_frames[self.facing][self.frame]
        if self.draw_shadow:
            self.shadow = self.shadow_frames[self.facing][self.frame]

    def set_coords(self, x: float, y: float):
        self.coords.xy = x, y
        self.rect.center = self.coords
        self.hitbox.center = self.coords + self.hitbox_offset

    def set_hitbox(self, width: float, height: float, offsetx: float = 0, offsety: float = 0):
        self.hitbox = self.rect.scale_by(width, height)
        self.hitbox_offset.xy = offsetx * self.rect.width, offsety * self.rect.height
        self.set_coords(*self.coords)

        self.rect_mask = pygame.mask.Mask(self.hitbox.size)
        self.rect_mask.fill()

    def animation(self):
        '''Handles animation'''

        # loops frames
        if self.loop_frames and self.frame >= len(self.animation_frames[self.facing]):
            self.frame = 0

        # set image
        if self.frame < len(self.animation_frames[self.facing]):
            self.image = self.animation_frames[self.facing][self.frame]
            if self.draw_shadow:
                self.shadow = self.shadow_frames[self.facing][self.frame]

            # determines whether the animation cooldown is over
            if (self.animation_cooldown
                    and pygame.time.get_ticks() - self.animation_time > self.animation_cooldown):

                self.animation_time = pygame.time.get_ticks()
                self.frame += 1

    def update(self):
        self.animation()