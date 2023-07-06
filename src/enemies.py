from constants import *
from projectiles import *
from entity import *
from sprite import Sprite

import pygame


class Ghost(MeleeEntity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Ghost'

        # hitbox
        self.set_hitbox(0.4, 0.5)

        # movement
        self.detection_distance = 350
        self.max_velocity = 3

        # stats
        self.exp = 25
        self.stats = Stats(100, 10, 10, 0.05, 0.05)

        # general animation
        self.set_animation('enemies/ghost', isFolder=True)

        # animation cooldown
        self.animation_cooldowns
        self.animation_cooldowns['idle'] = 1600 / \
            len(self.animation_frames[self.facing]['idle'])

        self.animation_cooldowns['run'] = self.animation_cooldowns['idle']
        self.animation_cooldowns['attack'] = (1200 - self.stats.speed) \
            / len(self.animation_frames[self.facing]['attack'])

        if self.animation_cooldowns['attack'] < 200:
            self.animation_cooldowns['attack'] = 200

        self.animation_cooldown = self.animation_cooldowns[self.action]

        # attack cooldown
        self.attack_cooldown = self.animation_cooldowns['attack']


class Mimic(MeleeEntity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Mimic'
        self.show_stats = False

        # hitbox
        self.hitbox = self.rect.scale_by(0.55, 0.45)

        # stats
        self.exp = 50
        self.stats = Stats(350, 0, 15, 0.25, 0)

        # animation
        self.set_animation('enemies/mimic', isFolder=True)

        # animation cooldown
        self.animation_cooldowns['idle'] = 1600 / \
            len(self.animation_frames[self.facing]['idle'])

        self.animation_cooldowns['run'] = self.animation_cooldowns['idle']
        self.animation_cooldowns['attack'] = (1200 - self.stats.speed) \
            / len(self.animation_frames[self.facing]['attack'])

        if self.animation_cooldowns['attack'] < 200:
            self.animation_cooldowns['attack'] = 200

        self.animation_cooldown = self.animation_cooldowns[self.action]

        # attack cooldown
        self.attack_cooldown = 200


class Sunflower(RangerEntity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Sunflower'
        self.show_stats = False

        # hitbox
        self.set_hitbox(0.25, 0.4)

        # range
        self.attack_range = 300

        # stats
        self.exp = 15
        self.stats = Stats(20, 0, 25, 0, 0)

        # general animation
        self.set_animation('enemies/sunflower', isFolder=True)

        # animation cooldown
        self.animation_cooldowns['idle'] = 1600 / \
            len(self.animation_frames[self.facing]['idle'])

        self.animation_cooldowns['run'] = self.animation_cooldowns['idle']
        self.animation_cooldowns['attack'] = (1200 - self.stats.speed) \
            / len(self.animation_frames[self.facing]['attack'])

        self.animation_cooldown = self.animation_cooldowns[self.action]

        # attack cooldown
        self.attack_cooldown = 1500

    def face_enemy(self, target: Sprite):
        # does not turn towards target
        pass

    def create_projectile(self, target):
        projectile_size = (max(*self.hitbox.size) * 2, ) * 2

        # creates projectile
        projectile = Fireball(
            self.hitbox.midtop,
            projectile_size,
            self.game,
            self.game.camera_group
        )

        projectile.set_target(
            target.hitbox.center,
            self.stats,
            self.game.player_group
        )


class Acorn(RangerEntity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Angry Acorn'

        # hitbox
        self.set_hitbox(0.5, 0.5)

        # movement & range
        self.detection_distance = 500
        self.attack_range = 250
        self.max_velocity = 4

        # stats
        self.exp = 35
        self.stats = Stats(30, 15, 10, 0.05, 0.05)

        # general animation
        self.set_animation('enemies/acorn', isFolder=True)

        # animation cooldown
        self.animation_cooldowns['idle'] = 600 / \
            len(self.animation_frames[self.facing]['idle'])

        self.animation_cooldowns['run'] = self.animation_cooldowns['idle']
        self.animation_cooldowns['attack'] = (1800 - self.stats.speed) \
            / len(self.animation_frames[self.facing]['attack'])

        self.animation_cooldown = self.animation_cooldowns[self.action]

        # attack cooldown
        self.attack_cooldown = 1500

    def create_projectile(self, target):
        projectile_size = (max(*self.hitbox.size), ) * 2

        # creates projectile
        projectile = AcornThorn(
            self.hitbox.center,
            projectile_size,
            self.game,
            self.game.camera_group
        )

        projectile.set_target(
            target.hitbox.center,
            self.stats,
            self.game.player_group
        )
