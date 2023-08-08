from constants import *
from projectiles import *
from entity import *
from sprite import Sprite

import pygame


class Ghost(MeleeEntity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Ghost'
        self.actions = ['idle', 'run', 'attack']

        # hitbox
        self.set_hitbox(0.25, 0.25)

        # stats
        self.exp = 25
        self.stats = Stats(100, 10, 15, 0.05, 0.05)

        # movement and range
        self.detection_distance = 350
        self.max_velocity = 2.5

        self.melee_range = max(self.hitbox.size) * 2.25

        # general animation
        self.set_animation('enemies/ghost', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}
        self.set_animation_cooldown(1200, 1200, 1400)

        # attack cooldown
        self.attack_cooldown = self.animation_cooldowns['attack']
        self.impact_frame = len(self.animation_frames[self.facing]['attack']) \
            - 3

        # smoke
        self.smoke_time = pygame.time.get_ticks()
        self.smoke_cooldown = 50

    def animation(self):
        super().animation()

        # draws smoke trail
        if pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            self.smoke_time = pygame.time.get_ticks()
            smoke_pos = list(self.hitbox.midbottom)
            smoke_pos[0] += random.randint(
                -self.hitbox.width // 4,
                self.hitbox.width // 4
            )

            if self.velocity.x:
                smoke_pos[0] += self.hitbox.width // 2 \
                    * -self.velocity.x / abs(self.velocity.x)

                smoke_pos[1] -= self.hitbox.height // 4

            # creates circle particle for smoke
            smoke = CircleParticle(
                smoke_pos,
                (randomize(self.hitbox.width * 0.7, 0.1),) * 2,
                self.game,
                self.game.camera_group
            )

            # smoke render
            smoke.animation_cooldown = 500
            smoke.fade_cooldown = 50
            smoke.color = random.choice((Color.ASH, Color.BLACK))

            smoke.set_circles()

            # smoke movement
            smoke.velocity.y = 0.2


class Mimic(MeleeEntity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Mimic'
        self.actions = ['idle', 'attack']
        self.show_stats = False

        # hitbox
        self.hitbox = self.rect.scale_by(0.55, 0.45)

        # stats
        self.exp = 50
        self.stats = Stats(350, 0, 25, 0.25, 0)

        # animation
        self.set_animation('enemies/mimic', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}
        self.set_animation_cooldown(1600, 1200)

        # attack cooldown
        self.attack_cooldown = 200
        self.impact_frame = len(self.animation_frames[self.facing]['attack']) \
            - 1


class Sunflower(RangerEntity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Sunflower'
        self.actions = ['idle', 'attack']
        self.show_stats = False

        # hitbox
        self.set_hitbox(0.25, 0.3)

        # stats
        self.exp = 15
        self.stats = Stats(20, 0, 30, 0, 0)

        # range
        self.attack_range = 250

        # general animation
        self.set_animation('enemies/sunflower', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}
        self.set_animation_cooldown(1600, 1200)

        # attack cooldown
        self.attack_cooldown = 1500
        self.impact_frame = 9

    def face_enemy(self, target: Sprite):
        # does not turn towards target
        pass

    def create_projectile(self, target):
        projectile_size = (self.hitbox.width * 2,) * 2

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
        self.actions = ['idle', 'run', 'attack']

        # hitbox
        self.set_hitbox(0.5, 0.5)

        # stats
        self.exp = 35
        self.stats = Stats(30, 15, 15, 0.1, 0.05)

        # movement and range
        self.detection_distance = 500
        self.max_velocity = 4
        self.attack_range = 250

        # general animation
        self.set_animation('enemies/acorn', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}
        self.set_animation_cooldown(600, 600, 1800)

        # attack cooldown
        self.attack_cooldown = 1500
        self.impact_frame = 5

    def create_projectile(self, target):
        projectile_size = (self.hitbox.width * 1.5,) * 2

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


class Newtshroom(RangerEntity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Newtshroom'
        self.actions = ['idle', 'run', 'attack']

        # hitbox
        self.set_hitbox(0.45, 0.425)

        # stats
        self.exp = 60
        self.stats = Stats(120, 10, 10, 0, 0)

        # movement and range
        self.detection_distance = 550
        self.max_velocity = 2
        self.attack_range = 375

        # general animation
        self.set_animation('enemies/newtshroom', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}
        self.set_animation_cooldown(800, 600, 1200)

        # attack cooldown
        self.attack_cooldown = 1200
        self.impact_frame = 6

    def create_projectile(self, target):
        projectile_size = (self.hitbox.width,) * 2

        # creates projectile
        for angle in range(-15, 30, 15):
            projectile = Spore(
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

            projectile.velocity = projectile.velocity.rotate(angle)

        # creates stomp dust
        dust_size = (self.hitbox.width,) * 2
        dust_pos = list(self.hitbox.midbottom)
        dust_pos[1] -= dust_size[1] / 4

        DustStomp(
            dust_pos,
            dust_size,
            self.game,
            self.game.camera_group
        )

