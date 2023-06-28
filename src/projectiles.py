from entity import Entity, Stats

import pygame
import math


class Projectile(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.target_group = None

        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = 300  # time for the particle to fade 10 alpha
        self.alpha = 255

        # attack
        self.stats = None

        self.pierce = 0
        self.max_pierce = 1

        self.damaged_targets = []

        # hitboxes are not used for collision
        self.set_hitbox(0, 0)
        
    def rotate_image(self):
        angle = 0
        if self.velocity.x != 0:
            angle = math.atan2(*self.velocity.yx)

        self.image = pygame.transform.rotate(self.image, angle * (180 / math.pi))
        self.image = pygame.transform.flip(self.image, False, True)

    def set_target(self, coords: list, stats: Stats, group: pygame.sprite.Group):
        self.stats = stats
        self.target_group = group

        self.velocity = pygame.math.Vector2(
            coords[0] - self.rect.centerx,
            coords[1] - self.rect.centery
        )

        self.velocity.scale_to_length(self.max_velocity)

        self.rotate_image()

    def collision(self):
        if abs(self.velocity.x) > 0 or abs(self.velocity.y) > 0:
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
            if (sprite not in self.damaged_targets and self.pierce < self.max_pierce):
                # checks if mask overlaps an enemy hitbox
                mask = pygame.mask.from_surface(self.image)
                offset = (sprite.hitbox.x - self.rect.x,
                      sprite.hitbox.y - self.rect.y)
                
                # damage is done to hitbox
                if mask.overlap(sprite.rect_mask, offset):
                    # inflict damage
                    sprite.hurt(self.stats)
                    
                    # piercing checks
                    self.pierce += 1
                    self.damaged_targets.append(sprite)

                    # fades faster when pierce count is reached
                    if self.pierce >= self.max_pierce:
                        self.fade_cooldown = 50
                        self.velocity.x, self.velocity.y = 0, 0
                        break

    def expire(self):
        '''Fades particle after its fade time
           Deletes the particle if it has no alpha'''
        if pygame.time.get_ticks() - self.fade_time > self.fade_cooldown:
            self.alpha -= 10
            if self.alpha > 0:
                self.image.set_alpha(self.alpha)

            else:
                self.kill()
                del self

    def update(self):
        self.movement()
        self.collision()
        self.hit_target()
        self.expire()


class SunBeam(Projectile):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.max_velocity = 7
        self.fade_cooldown = 500

        self.set_image('beam')


class AcornThorn(Projectile):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.max_velocity = 5
        self.fade_cooldown = 2000

        # hitboxes are not used for collision
        self.set_hitbox(0, 0)
        self.set_image('thorn')
        