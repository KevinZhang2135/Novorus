from constants import *

import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game = game

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2

    def center_target(self, target):
        self.offset.x = TILE_SIZE / 2
        self.offset.y = -TILE_SIZE / 2

        # stops scrolling screen when the player is past right edge of the screen
        if (target.rect.centerx >= self.game.level.size.x - self.half_width - TILE_SIZE / 2):
            self.offset.x = self.game.level.size.x \
                - self.display_surface.get_width() \
                - TILE_SIZE / 2

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.rect.centerx > self.half_width + TILE_SIZE / 2):
            self.offset.x = target.rect.centerx \
                - self.half_width

        # stops scrolling screen when the player is past bottom edge of the screen
        if (target.rect.centery >= self.game.level.size.y - self.half_height - TILE_SIZE / 2):
            self.offset.y = self.game.level.size.y \
                - self.display_surface.get_height() \
                - TILE_SIZE / 2

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.rect.centery > self.half_height - TILE_SIZE / 2):
            self.offset.y = target.rect.centery \
                - self.half_height \


    def custom_draw(self, player, show_hitboxes: bool = False):
        '''Draws the screen according to player movement'''
        self.center_target(player)
        # sorts sprites by sprite layer as primary and rectangle bottom as secondary
        for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.sprite_layer, sprite.hitbox.bottom)):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            # draws hitboxes
            if show_hitboxes:
                hitbox = pygame.Rect(
                    sprite.hitbox.x - self.offset.x,
                    sprite.hitbox.y - self.offset.y,
                    sprite.hitbox.width,
                    sprite.hitbox.height
                )

                pygame.draw.rect(
                    self.display_surface,
                    (255, 0, 0),
                    hitbox,
                    1
                )

    def update(self):
        "Updates all sprites"
        for sprite in self.sprites():
            if (abs(self.game.player.rect.centerx
                    - sprite.rect.centerx
                    + sprite.rect.width) < self.half_width

                or abs(self.game.player.rect.centery
                       - sprite.rect.centery
                       + sprite.rect.height) < self.half_height):

                sprite.update()
