from constants import *

import pygame


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

        self.sprite_layer = 0

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

