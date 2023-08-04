from constants import *
from color import Color
import pygame

class LightGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.game = game
