from entity import Entity

import pygame

class Projectile(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.target_group = None

        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = 300 # time for the particle to fade 10 alpha
        self.alpha = 255

        # attack
        self.attack = 0
        self.pierce = 0
        self.max_pierce = 1

    def set_target_group(self, group: pygame.sprite.Group):
        self.target_group = group

    def set_attack(self, attack):
        self.attack = attack

    def hit_target(self):
        for sprite in pygame.sprite.spritecollide(self, self.target_group, False):
            self.pierce += 1
            sprite.stats.health -= self.attack
            if self.pierce >= self.max_pierce:
                self.kill()
                del self
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
        self.set_image('slash')
        self.set_hitbox(0.4, 0.5, offsetx=0.05, offsety=-0.05)


        