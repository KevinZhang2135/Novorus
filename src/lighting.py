from constants import *
from entity import *

import pygame



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
        self.color = WHITE

    def render_lighting(self):
        self.filter.fill(self.color)

        for sprite in self.sprites():
            # centers light on sprite according to player view
            offset_pos = sprite.rect.topleft \
                - self.game.camera_group.offset \
                + list(map(lambda x: x / 2, sprite.rect.size)) \
                - sprite.light_size / 2

            self.filter.blit(sprite.light, offset_pos)

        #draws screen filter
        self.display_surface.blit(
            self.filter,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
        )
