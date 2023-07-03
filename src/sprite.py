from constants import *

import pygame
import math


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

        # masks
        self.rect_mask = pygame.mask.Mask(self.hitbox.size)
        self.rect_mask.fill()

        # render
        self.sprite_layer = 0

        # animation
        self.frame = 0
        self.loop_frames = True

        self.animation_cooldown = 0
        self.animation_time = pygame.time.get_ticks()
        self.animation_frames = []

        # shadows
        self.draw_shadows = False
        self.shadows = []

    def set_image(self, image_file: str):
        self.image = IMAGES[image_file].copy()
        self.image = pygame.transform.scale(self.image, self.size)
        self.sprite_mask = pygame.mask.from_surface(self.image)

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

    def set_animation(self, filepath: str):
        num_of_frames = len(os.listdir(
            f'{SPRITE_PATH}/{filepath}'
        ))

        for i in range(num_of_frames):
            image = IMAGES[f"{filepath.split('/')[-1]}{i + 1}"].copy()
            image = pygame.transform.scale(
                image,
                self.rect.size
            )

            self.animation_frames.append(image)

        # sets image
        self.image = self.animation_frames[self.frame]

    def update_shadow(self):
        if self.draw_shadows:
            mask = pygame.mask.from_surface(self.image)
            mask = [(x + self.rect.x + 100, y + self.rect.y + 100)
                    for x, y in mask.outline()]
            
            self.shadows = mask

            # self.shadows.clear()
            # for x, y in mask:
            #     shadow_height = 0
            #     shadow_width = 0
            #     self.shadows.append((x + shadow_width, y + shadow_height))

    def animation(self):
        '''Handles animation'''

        # loops frames
        if self.frame >= len(self.animation_frames) and self.loop_frames:
            self.frame = 0

        # set image
        if self.frame < len(self.animation_frames):
            self.image = self.animation_frames[self.frame]

            # determines whether the animation cooldown is over
            if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
                self.animation_time = pygame.time.get_ticks()
                self.frame += 1
