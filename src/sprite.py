import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(groups)
        self.game = game

        self.coords = pygame.math.Vector2()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center=coords)
        self.hitbox = pygame.Rect(self.rect)

        self.sprite_layer = 0