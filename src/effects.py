from constants import *

import pygame

class TextPopUp:
    def __init__(self, text, rect):
        self.text = text
        self.rect = rect

        self.alpha = 255

        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)

        self.time = pygame.time.get_ticks()
        self.expiration_time = randomize(1000, 0.1)

    def movement(self):
        '''Moves the text vertically'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        # movement decay when the speed is low
        if abs(self.velocity.x) < 0.25:
            self.velocity.x = 0

        if abs(self.velocity.y) < 0.25:
            self.velocity.y = 0

        self.rect.center += self.velocity

    def expire(self):
        '''Fades text after its expiration time'''
        if pygame.time.get_ticks() - self.time > self.expiration_time:
            self.alpha -= 10
            if self.alpha > 0:
                self.text.set_alpha(self.alpha)

    def update(self):
        '''Handles events'''
        self.movement()
        self.expire()


class Particle(pygame.sprite.Sprite):
    def __init__(self, coords, size, image, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.alpha = 255
        self.image = IMAGES[image].copy()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)

        self.time = pygame.time.get_ticks()
        self.expiration_time = randomize(1000, 0.1)

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

        self.rect.center += self.velocity

    def expire(self):
        '''Deletes particle after its expiration time'''
        if pygame.time.get_ticks() - self.time > self.expiration_time:
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


class LightSources(pygame.sprite.Group):
    def __init__(self, resolution):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2
        self.resolution = resolution

        self.filter = pygame.surface.Surface(self.resolution)

        # light offset
        self.offset = pygame.math.Vector2()
        self.sprite_layer = 3
        self.color = LIGHT_GREY

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def render_lighting(self, player):
        self.filter.fill(self.color)
        self.center_target(player)
        for sprite in self.sprites():
            if (abs(player.rect.left - sprite.rect.left) < self.half_width
                    or abs(player.rect.top - sprite.rect.top) < self.half_height):
                offset_pos = sprite.rect.topleft \
                    - self.offset \
                    + list(map(lambda x: x / 2, sprite.rect.size)) \
                    - sprite.light_size / 2

                self.filter.blit(sprite.light, offset_pos)

        self.display_surface.blit(
            self.filter,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)

