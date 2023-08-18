from constants import *
from sprite import Sprite
from particles import *
from projectiles import *

import pygame


class SpellGroup(pygame.sprite.GroupSingle):
    def __init__(self, game):
        super().__init__()
        self.game = game

class Spell(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.cast_time = pygame.time.get_ticks()
        self.cast_duration = 1000

        self.cost = 0

    def cast(self, coords, stats):
        '''Creates a projectile at coords'''
        pass

class EarthShaker(Spell):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.cast_duration = 1000
        self.cost = 50

    def cast(self, coords: list, stats: Stats, group):
        '''Creates a projectile at coords'''
        Projectile()


