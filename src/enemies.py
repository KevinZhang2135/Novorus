from constants import *
from projectiles import *
from entity import *
from sprite import Sprite

import pygame


class Ghost(MeleeEntity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Ghost'

        # hitbox
        self.set_hitbox(0.25, 0.25)
        self.set_collision_box(0.25, 0.25)

        # stats
        self.stats = Stats(80, 10, 15, 0.05, 0.05)

        # movement and range
        self.detection_distance = 350
        self.max_velocity = 2.5

        self.melee_range = max(self.hitbox.size) * 2.25

        # general animation
        self.animation_cooldowns = {
            'idle': 200,
            'run': 200,
            'attack': 200
        }

        self.set_animation('enemies/ghost', isFolder=True)

        # attack cooldown
        self.attack_cooldown = self.animation_cooldowns['attack']
        self.impact_frame = len(self.animation_frames[self.facing]['attack']) \
            - 3

        # smoke
        self.smoke_time = pygame.time.get_ticks()
        self.smoke_cooldown = 50

    def animation(self):
        super().animation()

        # does not draw smoke unless time elapsed exceeds cooldown
        if not pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            return
    
        # draws smoke trail and randomizes position
        self.smoke_time = pygame.time.get_ticks()
        smoke_pos = list(self.hitbox.midbottom)
        smoke_pos[0] += random.randint(
            -self.hitbox.width // 4,
            self.hitbox.width // 4
        )

        if self.velocity.x:
            # draws smoke in the opposite bottom corner to movement
            smoke_pos[0] += self.hitbox.width // 2 \
                * -signum(self.velocity.x)

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

        # hitbox
        self.set_hitbox(0.55, 0.45)
        self.set_collision_box(0.55, 0.45)

        # stats
        self.stats = Stats(350, 0, 25, 0.25, 0)

        # movement and range
        self.melee_range = max(self.hitbox.size) * 5

        # animation
        self.animation_cooldowns = {
            'idle': 0,
            'attack': 1200
        }

        self.set_animation('enemies/mimic', isFolder=True)

        # attack cooldown
        self.attack_cooldown = 200
        self.impact_frame = len(self.animation_frames[self.facing]['attack']) \
            - 1


class Sunflower(RangerEntity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Sunflower'

        # hitbox
        self.set_hitbox(0.25, 0.3)
        self.set_collision_box(0.25, 0.3)

        # stats
        self.stats = Stats(20, 0, 30, 0, 0)

        # range
        self.attack_range = 250

        # general animation
        self.animation_cooldowns = {
            'idle': 0,
            'attack': 0
        }

        self.set_animation('enemies/sunflower', isFolder=True)

        # attack cooldown
        self.attack_cooldown = 5000
        self.impact_frame = 0

    def face_enemy(self, target: Sprite):
        # does not turn towards target
        pass

    def create_projectile(self, target):
        projectile_size = (self.hitbox.height * 2,) * 2
        projectile_pos = list(self.hitbox.midtop)
        projectile_pos[1] -= self.hitbox.height / 2

        # creates projectile
        projectile = SunCharge(
            projectile_pos,
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
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Angry Acorn'

        # hitbox
        self.set_hitbox(0.5, 0.5)
        self.set_collision_box(0.5, 0.5)

        # stats
        self.stats = Stats(30, 15, 15, 0.1, 0.05)

        # movement and range
        self.detection_distance = 500
        self.max_velocity = 4
        self.attack_range = 250

        # general animation
        self.animation_cooldowns = {
            'idle': 100,
            'run': 100,
            'attack': 100
        }

        self.set_animation('enemies/acorn', isFolder=True)

        # attack cooldown
        self.attack_cooldown = 1500
        self.impact_frame = 6

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
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Newtshroom'

        # hitbox
        self.set_hitbox(0.45, 0.425)
        self.set_collision_box(0.45, 0.2, offsety=0.1)

        # stats
        self.stats = Stats(100, 10, 10, 0, 0)

        # movement and range
        self.detection_distance = 550
        self.max_velocity = 2
        self.attack_range = 375

        # general animation
        self.animation_cooldowns = {
            'idle': 200,
            'run': 100,
            'attack': 120
        }

        self.set_animation('enemies/newtshroom', isFolder=True)

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

