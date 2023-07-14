from constants import pygame
from constants import *
from sprite import Sprite

import pygame


class Particle(Sprite):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        # movement
        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()

        # render
        self.alpha = 255
        self.sprite_layer = 5

        # fade
        self.fade = True
        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = randomize(1000, 0.1)

        # hitboxes are not used for collision
        self.set_hitbox(0, 0)
        
    def movement(self):
        '''Handles movement'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

    def expire(self):
        '''Fades particle after its fade time
           Deletes the particle if it has no alpha'''
        if pygame.time.get_ticks() - self.fade_time > self.fade_cooldown:
            self.alpha -= 10
            if self.alpha > 0 and self.fade:
                self.image.set_alpha(self.alpha)

            else:
                self.kill()
                del self

    def update(self):
        '''Handles events'''
        self.movement()
        self.animation()
        self.expire()


class Explosion(Particle):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.loop_frames = False
        self.animation_cooldown = 100

        self.set_animation('particles/explosion', isFolder=True)

class Dust(Particle):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.set_animation(f'particles/dust/dust{random.randint(1, 3)}')
        self.velocity.y = -2

class DustTrail(Particle):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.loop_frames = False
        self.animation_cooldown = 100

        self.set_animation('particles/dust_trail', isFolder=True)

class TextPopUp(Particle):
    def __init__(self, coords: list, game, group: pygame.sprite.Group):
        super().__init__(coords, [0, 0], game, group)

    def set_text(self, text):
        self.image = text
        self.rect = self.image.get_rect(center=self.coords)
        self.hitbox = pygame.Rect(self.rect)
