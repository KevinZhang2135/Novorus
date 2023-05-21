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
        self.fade_time = randomize(1000, 0.1)

    def movement(self):
        '''Moves the text'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        # movement decay when the speed is low
        if abs(self.velocity.y) < 0.25:
            self.velocity.y = 0

        self.rect.center += self.velocity

    def expire(self):
        '''Fades text after its fade time'''
        if pygame.time.get_ticks() - self.time > self.fade_time:
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
        self.fade_time = randomize(1000, 0.1) # time for the particle to fade 10 alpha

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


class LightGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.resolution = self.game.resolution

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

        self.display_surface.blit(
            self.filter,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)

