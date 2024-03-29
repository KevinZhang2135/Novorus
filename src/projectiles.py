from constants import *
from particles import *
from entity import *

import pygame


class Projectile(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.facing = 'right'
        self.target_group = None

        # render
        self.alpha = 255
        self.angle = 0

        # fade
        self.fade = True
        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = 300

        # attack
        self.stats = None

        self.pierce = 0
        self.max_pierce = 1
        self.damaged_targets = []

        # hitboxes are not used for collision
        self.set_hitbox(0, 0)

        # shadows
        self.draw_shadow = False

    def rotate_image(self):
        if self.pierce < self.max_pierce:
            self.angle = 0
            if self.velocity.x != 0:
                self.angle = math.atan2(*self.velocity.yx)

            elif self.velocity.y > 0:
                self.angle = math.pi / 2

            elif self.velocity.y < 0:
                self.angle = math.pi * 3 / 2

        if self.angle:
            self.image, self.rect = rotate_center(
                self.image,
                self.angle * (180 / math.pi),
                self.rect
            )

            self.image = pygame.transform.flip(self.image, False, True)

    def set_target(self, coords: list, stats: Stats, target_group):
        self.stats = stats
        self.target_group = target_group
        
        if self.max_velocity:
            self.velocity = pygame.math.Vector2(
                coords[0] - self.rect.centerx,
                coords[1] - self.rect.centery
            )

            self.velocity.scale_to_length(self.max_velocity)

    def collision(self):
        # does not check collision unless speed is greater than 0
        if not self.velocity.magnitude():
            return
        
        # sorts sprites by distance
        sprites = pygame.sprite.spritecollide(
            self,
            self.game.collision_group,
            False
        )

        sprites.sort(key=lambda sprite: math.dist(
            self.hitbox.center,
            sprite.hitbox.center
        ))

        for sprite in sprites:
            # minimum distance between two sprites which includes collision
            collision_distance = pygame.math.Vector2(
                (self.hitbox.width + sprite.hitbox.width) / 2,
                (self.hitbox.height + sprite.hitbox.height) / 2
            )

            # distance between the centers of two sprites
            center_distance = pygame.math.Vector2(
                self.hitbox.centerx - sprite.hitbox.centerx,
                self.hitbox.centery - sprite.hitbox.centery
            )

            # checks if the distance of the sprites are within collision distance
            if (abs(center_distance.x) < collision_distance.x
                    and abs(center_distance.y) < collision_distance.y):

                self.velocity.xy = 0, 0
                self.fade_cooldown = 0
                break

    def hit_target(self):
        # checks if the rect overlaps an enemy rect
        collided_targets = self.rect.collideobjectsall(
            self.target_group.sprites()
        )

        # sorts sprites by distance
        closest_targets = sorted(
            collided_targets,
            key=lambda target: self.coords.distance_to(target.rect.center)
        )

        for sprite in closest_targets:
            # target can only be damaged once by a projectile
            if (sprite not in self.damaged_targets 
                    and (self.pierce < self.max_pierce or self.max_pierce == -1)):
                # checks if mask overlaps an enemy hitbox
                mask = pygame.mask.from_surface(self.image)
                offset = (
                    sprite.hitbox.x - self.rect.x,
                    sprite.hitbox.y - self.rect.y
                )

                # damage is done to hitbox
                if mask.overlap(sprite.rect_mask, offset):
                    # inflict damage
                    sprite.hurt(self.stats)

                    # piercing checks
                    self.pierce += 1
                    self.damaged_targets.append(sprite)

                    # fades faster when pierce count is reached
                    # infinite pierce when max_pierce is -1
                    if self.pierce >= self.max_pierce and self.max_pierce != -1:
                        self.fade_cooldown = 50
                        self.velocity.xy = 0, 0
                        break

    def expire(self):
        '''Fades particle after its fade time
           Deletes the particle if it has no alpha'''
        if pygame.time.get_ticks() - self.fade_time > self.fade_cooldown:
            self.alpha -= 8
            if self.alpha < 0 or not self.fade:
                self.kill()
                del self

    def animation(self):
        self.animation_cooldown = self.animation_cooldowns[self.action]

        # loops frames
        if self.loop_frames and self.frame >= len(self.animation_frames[self.facing][self.action]):
            self.frame = 0

        # set image
        if self.frame < len(self.animation_frames[self.facing][self.action]):
            self.image = self.animation_frames[self.facing][self.action][self.frame]
            self.rotate_image()

            if self.draw_shadow:
                self.shadow = self.shadow_frames[self.facing][self.action][self.frame]

            # determines whether the animation cooldown is over
            if (self.animation_cooldown
                    and pygame.time.get_ticks() - self.animation_time > self.animation_cooldown):

                self.animation_time = pygame.time.get_ticks()
                self.frame += 1
        
        self.image.set_alpha(self.alpha)

    def update(self):
        self.movement()
        self.collision()
        self.hit_target()
        self.expire()
        self.animation()


class SunCharge(Projectile):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.loop_frames = False
        self.fade_cooldown = 700

        # general animation
        self.animation_cooldowns = {'idle': 130}
        self.set_animation('projectiles/sun_charge', isFolder=True)

        # light
        self.draw_light = True
        self.light_color = Color.GOLD
        self.light_radius = 20

    def kill(self):
        super().kill()

        targets = self.target_group.sprites()
        if targets:
            target = sorted(
                targets,
                key=lambda sprite: math.dist(self.coords, sprite.hitbox.center)
            )[0]

            fireball = Fireball(
                self.coords,
                self.size,
                self.game,
                self.game.camera_group
            )

            fireball.set_target(
                target.hitbox.center,
                self.stats,
                self.target_group
            )

    def update(self):
        self.expire()
        self.animation()


class Fireball(Projectile):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.fade = False
    
        self.fade_cooldown = 2500
        self.max_velocity = 3

        # general animation
        self.animation_cooldowns = {'idle': 200}
        self.set_animation('projectiles/fireball', isFolder=True)

        # light
        self.draw_light = True
        self.light_color = Color.GOLD
        self.light_radius = 30

    def kill(self):
        # leaves explosion on death
        super().kill()
        Explosion1(
            self.rect.center,
            self.rect.size,
            self.game,
            self.game.camera_group
        )


class AcornThorn(Projectile):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.fade_cooldown = 2000
        self.max_velocity = 5
        
        # general animation
        self.set_animation('projectiles/thorn', isFolder=True)


class Spore(Projectile):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.fade_cooldown = 2000
        self.max_velocity = 4

        # general animation
        self.animation_cooldowns = {'idle': 250}
        self.set_animation('projectiles/spore', isFolder=True)


class EarthExplosion(Projectile):
    def __init__(self, coords: list, size: list, game, group):
        super().__init__(coords, size, game, group)
        self.loop_frames = False
        self.fade_cooldown = 700
        self.max_pierce = -1

        # general animation
        self.animation_cooldowns = {'idle': 100}
        self.set_animation('projectiles/earthshaker', isFolder=True)

    def update(self):
        self.hit_target()
        self.expire()
        self.animation()
        