from constants import *
from effects import *
from entity import *
from projectiles import *

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
        self.set_animation('enemies/ghost')
        self.image = self.animation_types['idle'][self.frame]
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
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
        self.set_animation('enemies/mimic')
        self.image = self.animation_types['idle'][self.frame]
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
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
        self.set_animation('enemies/sunflower')
        self.image = self.animation_types['idle'][self.frame]
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown


class Acorn(RangerEnemy):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Angry Acorn'

        # hitbox
        self.set_hitbox(0.5, 0.5)

        # movement
        self.detection_distance = 700
        self.attack_range = 500
        self.max_velocity = 3.5

        # stats
        self.exp = 30
        self.exp_levels = None

        self.stats = Stats(10, 10, 8, 0.15, 0.15)

        # general animation
        self.set_animation('enemies/acorn')
        self.image = self.animation_types['idle'][self.frame]
        self.animation_cooldown = 600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_cooldown = (randomize(1800, 0.25) - self.stats.speed) \
            / len(self.animation_types['attack'])

        self.cooldown = self.animation_cooldown

    def attack_enemy(self, target_group: pygame.sprite.Group):
        # checks if the target rect is within attack range
        targets = target_group.sprites()
        targets.sort(key=lambda sprite: dist(
            self.hitbox.center,
            sprite.hitbox.center
        ))

        # attacks when target is within attack range
        if (len(targets) > 0
                and dist(self.hitbox.center, targets[0].hitbox.center) < self.attack_range):
            self.in_combat = True
            self.cooldown = self.attack_cooldown
            
            # only attacks the last frame
            if (pygame.time.get_ticks() - self.attack_time > self.attack_cooldown):
                # trigger attack animation
                if not self.attacking:
                    self.frame = 0
                    self.attacking = True

                # shoot projectile after animation ends
                if (self.frame == len(self.animation_types['attack'])):
                    self.attack_time = pygame.time.get_ticks()
                    self.attacking = False

                    projectile_size = (min(*self.hitbox.size), ) * 2

                    # creates projectile
                    projectile = AcornThorn(self.hitbox.center, projectile_size, self.game, self.game.camera_group)
                    projectile.set_target(self.game.player_group)
                    projectile.set_attack(self.stats)
                    projectile.set_vector(targets[0].hitbox.center)
                    

        # cancels attack when target moves outside attack range
        else:
            self.attacking = False
            self.in_combat = False
            self.cooldown = self.animation_cooldown
                