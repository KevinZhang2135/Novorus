import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(groups)
        self.game = game

        self.coords = pygame.math.Vector2(*coords)
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center=coords)
        self.hitbox = pygame.Rect(self.rect)

        self.sprite_layer = 0

    def set_coords(self, x, y):
        self.coords.xy = x, y
        self.rect.center = self.coords
        self.hitbox.center = self.coords
        