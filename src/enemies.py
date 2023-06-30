from constants import *
from lighting import *
from projectiles import *
from entity import *
from sprite import Sprite

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

        self.stats = Stats(30, 10, 4, 0.05, 0.1)

        # general animation
        self.set_animation('enemies/ghost')
        self.animation_cooldown = 1600 / len(self.animation_frames['idle'])
        self.cooldown = self.animation_cooldown

        # attack speed and animation
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_frames['attack'])

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200


class Mimic(MeleeEnemy):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Mimic'
        self.show_stats = False

        # stats
        self.exp = 50

        self.stats = Stats(300, 0, 15, 0.25, 0)

        # animation
        self.set_animation('enemies/mimic')
        self.animation_cooldown = 1600 / len(self.animation_frames['idle'])
        self.cooldown = self.animation_cooldown

        # attack speed and animation
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_frames['attack'])

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200


class Sunflower(RangerEnemy):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Sunflower'
        self.show_stats = False

        # hitbox
        self.set_hitbox(0.25, 0.4)

        # range
        self.attack_range = 300

        # stats
        self.exp = 5

        self.stats = Stats(20, 0, 15, 0, 0)

        # general animation
        self.set_animation('enemies/sunflower')
        self.animation_cooldown = 1600 / len(self.animation_frames['idle'])
        self.cooldown = self.animation_cooldown

        # attack speed and animation
        self.attack_cooldown = (2400 - self.stats.speed) \
            / len(self.animation_frames['attack'])

    def face_enemy(self, target: Sprite):
        # does not turn towards target
        pass

    def create_projectile(self, target):
        projectile_size = (max(*self.hitbox.size) * 2, ) * 2

        # creates projectile
        projectile = Fireball(
            self.hitbox.midtop, projectile_size, self.game, self.game.camera_group)
        projectile.set_target(
            target.hitbox.center,
            self.stats,
            self.game.player_group
        )


class Acorn(RangerEnemy):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Angry Acorn'

        # hitbox
        self.set_hitbox(0.5, 0.5)

        # movement & range
        self.detection_distance = 700
        self.attack_range = 1500
        self.max_velocity = 3.5

        # stats
        self.exp = 30

        self.stats = Stats(10, 15, 8, 0.15, 0.1)

        # general animation
        self.set_animation('enemies/acorn')
        self.animation_cooldown = 700 / len(self.animation_frames['idle'])
        self.cooldown = self.animation_cooldown

        # attack speed and animation
        self.attack_cooldown = (1400 - self.stats.speed) \
            / len(self.animation_frames['attack'])
        

    def create_projectile(self, target):
        projectile_size = (max(*self.hitbox.size), ) * 2

        # creates projectile
        projectile = AcornThorn(
            self.hitbox.center, projectile_size, self.game, self.game.camera_group)
        projectile.set_target(
            target.hitbox.center,
            self.stats,
            self.game.player_group
        )
