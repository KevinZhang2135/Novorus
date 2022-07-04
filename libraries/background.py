import pygame
import random

from libraries.tools import *

class Ambience(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, image: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image(image, size)
        self.rect = self.image.get_rect(center=coords)

        if random.randint(0, 1):
            self.image = pygame.transform.flip(self.image, True, False)