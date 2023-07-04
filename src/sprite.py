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

        # render
        self.sprite_layer = 0

        # animation
        self.frame = 0
        self.loop_frames = True

        self.animation_cooldown = 0
        self.animation_time = pygame.time.get_ticks()
        self.animation_frames = []

        # masks
        self.rect_mask = pygame.mask.Mask(self.hitbox.size)
        self.rect_mask.fill()

        # shadows
        self.draw_shadow = False
        self.shadow = []

    def set_image(self, image_file: str):
        self.image = IMAGES[image_file].copy()
        self.image = pygame.transform.scale(self.image, self.size)

    def set_animation(self, filepath: str):
        for path in os.listdir(f'{SPRITE_PATH}/{filepath}'):
            image = IMAGES[path[:-4]].copy()
            image = pygame.transform.scale(
                image,
                self.rect.size
            )

            self.animation_frames.append(image)

        # sets image
        self.image = self.animation_frames[self.frame]

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
        if self.frame >= len(self.animation_frames) and self.loop_frames:
            self.frame = 0

        # set image
        if self.frame < len(self.animation_frames):
            self.image = self.animation_frames[self.frame]

            # determines whether the animation cooldown is over
            if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
                self.animation_time = pygame.time.get_ticks()
                self.frame += 1

    def set_shadow(self):
        '''Experimental'''
        if self.draw_shadow:
            mask = pygame.mask.from_surface(self.image).outline(every=2)
            mask = [(x + self.rect.x, y + self.rect.y)
                    for x, y in mask]
            
            self.shadow.clear()
            for x, y in mask:
                shadow_height = (self.hitbox.bottom - y) * 0.5
                shadow_width = shadow_height * math.tan(math.pi * 1 / 3)
                self.shadow.append((x + shadow_width, y + shadow_height))
