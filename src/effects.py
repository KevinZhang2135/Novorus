from constants import *
from entity import *
from sprite import Sprite

import pygame


class Particle(Sprite):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()

        self.time = pygame.time.get_ticks()
        self.fade_time = randomize(1000, 0.1) # time for the particle to fade 10 alpha

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

    def set_image(self, image):
        super().set_image(image, self.size)

    def expire(self):
        '''Fades particle after its fade time
           Deletes the particle if it has no alpha'''
        if pygame.time.get_ticks() - self.time > self.fade_time:
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


class LightGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.resolution = self.game.resolution

        # screen color filter
        self.filter = pygame.surface.Surface(self.resolution)

        # light offset
        self.offset = pygame.math.Vector2()
        self.sprite_layer = 3
        self.color = LIGHT_GREY

    def render_lighting(self):
        self.filter.fill(self.color)

        for sprite in self.sprites():
            # centers light on sprite according to player view
            offset_pos = sprite.rect.topleft \
                - self.game.camera_group.offset \
                + list(map(lambda x: x / 2, sprite.rect.size)) \
                - sprite.light_size / 2

            self.filter.blit(sprite.light, offset_pos)

        # darws screen filter
        self.display_surface.blit(
            self.filter,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
        )
