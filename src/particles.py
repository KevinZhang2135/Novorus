from constants import *
from sprite import Sprite

import pygame

class Particle(Sprite):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()

        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = randomize(1000, 0.1) # time for the particle to fade 10 alpha

        self.alpha = 255
        self.sprite_layer = 3

    def movement(self):
        '''Handles movement'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        # movement decay when the speed is low
        if abs(self.velocity.x) < 0.25:
            self.velocity.x = 0

        if abs(self.velocity.y) < 0.25:
            self.velocity.y = 0

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

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
        '''Handles events'''
        self.movement()
        self.expire()


class TextPopUp(Particle):
    def __init__(self, coords: list, game, group: pygame.sprite.Group):
        super().__init__(coords, [0, 0], game, group)

    def set_text(self, text):
        self.image = text
        self.rect = self.image.get_rect(center=self.coords)
        self.hitbox = pygame.Rect(self.rect)