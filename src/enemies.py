from constants import *
from effects import *
from entity import *

import pygame


class Ghost(MeleeEnemy):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.name = 'Ghost'
        
        # hitbox
        self.set_hitbox(0.4, 0.5)

        # movement
        self.detection_distance = 350
        self.max_velocity = 2

        # stats
        self.exp = 15
        self.exp_levels = None

        self.stats = Stats(30, 10, 4, 0.05, 0.1)

        # general animation
        self.frame = 0
        self.set_animation('enemies/ghost')
        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown


class Mimic(MeleeEnemy):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.name = 'Mimic'
        self.show_stats = False

        # stats
        self.exp = 50
        self.exp_levels = False

        self.stats = Stats(100, 20, 7, 0.15, 0)

        # animation
        self.frame = 0
        self.set_animation('enemies/mimic')
        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])
        

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown


class Sunflower(MeleeEnemy):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.name = 'Sunflower'
        self.show_stats = False

        # hitbox
        self.set_hitbox(0.4, 0.9)

        # stats
        self.exp = 5
        self.exp_levels = False

        self.stats = Stats(20, 5, 3, 0.05, 0)

        # general animation
        self.frame = 0
        self.set_animation('enemies/sunflower')
        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])
        
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown


class Acorn(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        
        self.name = 'Acorn Thrower'

        # hitbox
        self.set_hitbox(0.4, 0.5)

        # movement
        self.detection_distance = 450
        self.max_velocity = 3

        # stats
        self.exp = 15
        self.exp_levels = None

        self.stats = Stats(30, 10, 4, 0.05, 0.1)

        # general animation
        self.frame = 0
        self.set_animation('enemies/acorn')
        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown