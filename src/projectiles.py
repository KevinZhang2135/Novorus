from entity import Entity

import pygame


class Projectile(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.target_group = None

        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = 300  # time for the particle to fade 10 alpha
        self.alpha = 255

        # attack
        self.attack = 0
        self.crit_chance = 0

        self.pierce = 0
        self.max_pierce = 1

        self.damaged_targets = []

    def set_target_group(self, group: pygame.sprite.Group):
        self.target_group = group

    def set_attack(self, stats):
        self.attack = stats.attack
        self.crit_chance = stats.crit_chance

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
                    sprite.hurt(self.attack, self.crit_chance)
                    
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
        self.expire()
        self.hit_target()


class SwordSlash(Projectile):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.fade_cooldown = 100
        self.max_pierce = 3

        self.set_image('slash')

    def movement(self):
        self.velocity *= 0.9
        if abs(self.velocity.x) < self.max_velocity / 10:
            self.velocity.x = 0

        if abs(self.velocity.y) < self.max_velocity / 10:
            self.velocity.y = 0

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )
