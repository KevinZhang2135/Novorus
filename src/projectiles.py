from entity import Entity

import pygame
from math import dist


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

    def set_vector(self, coords):
        self.acceleration = pygame.math.Vector2(
            coords[0] - self.rect.centerx,
            coords[1] - self.rect.centery
        )

        self.acceleration.scale_to_length(self.max_velocity)
        self.velocity += self.acceleration

    def set_target(self, group: pygame.sprite.Group):
        self.target_group = group

    def set_attack(self, stats):
        self.stats = stats

    def collision(self):
        if abs(self.velocity.x) > 0 or abs(self.velocity.y) > 0:
            # sorts sprites by distance
            sprites = pygame.sprite.spritecollide(
                self,
                self.game.collision_group,
                False
            )
            
            sprites.sort(key=lambda sprite: dist(
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
        collided_targets = self.hitbox.collideobjectsall(
            self.target_group.sprites()
        )[:self.max_pierce]

        closest_targets = sorted(
            collided_targets,
            key=lambda target: self.coords.distance_to(target.rect.center)
        )

        for sprite in closest_targets:
            if (sprite not in self.damaged_targets and self.pierce < self.max_pierce):
                # mask collision
                if (pygame.sprite.collide_mask(self, sprite)):
                    # inflict damage
                    sprite.hurt(self.stats)
                    
                    # piercing checks
                    self.pierce += 1
                    self.damaged_targets.append(sprite)

                    # fades faster when pierce count is reached
                    if self.pierce >= self.max_pierce:
                        self.fade_cooldown = 100
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


class AcornThorn(Projectile):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.max_velocity = 7
        self.fade_cooldown = 3000

        self.set_hitbox(0.2, 0.2)
        self.set_image('thorn')
        