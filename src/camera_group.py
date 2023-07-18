from constants import *

import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.screen.get_width() / 2
        self.half_height = self.screen.get_height() / 2

    def center_target(self, target):
        self.offset.x = -TILE_SIZE / 2
        self.offset.y = -TILE_SIZE / 2

        # stops scrolling screen when the player is past right edge of the screen
        if (target.rect.centerx >= self.game.level.size.x - self.half_width):
            self.offset.x = self.game.level.size.x \
                - self.screen.get_width() \
                - TILE_SIZE / 2

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.rect.centerx > self.half_width):
            self.offset.x = target.rect.centerx \
                - self.half_width \
                - TILE_SIZE / 2

        # stops scrolling screen when the player is past bottom edge of the screen
        if (target.rect.centery >= self.game.level.size.y - self.half_height - TILE_SIZE / 2):
            self.offset.y = self.game.level.size.y \
                - self.screen.get_height() \
                - TILE_SIZE / 2

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.rect.centery > self.half_height - TILE_SIZE / 2):
            self.offset.y = target.rect.centery \
                - self.half_height

    def render(self, show_hitboxes: bool = False, show_rects: bool = False):
        '''Draws the screen according to player movement'''
        self.center_target(self.game.player)

        # sorts sprites by sprite layer as primary and rectangle bottom as secondary
        for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.sprite_layer, sprite.hitbox.bottom)):
            if sprite.draw_shadow and sprite.shadow:
                shadow_pos = sprite.hitbox.bottomleft - self.offset
                shadow_pos.y -= sprite.shadow.surface.get_height()
                self.screen.blit(sprite.shadow.surface, shadow_pos)

            offset_pos = sprite.rect.topleft - self.offset
            self.screen.blit(sprite.image, offset_pos)

            # draws sprite hitboxes
            show_hitboxes and self.draw_hitboxes(sprite)

            # draws sprite rects
            show_rects and self.draw_rects(sprite)

    def draw_hitboxes(self, sprite):
        hitbox = pygame.Rect(
            sprite.hitbox.x - self.offset.x,
            sprite.hitbox.y - self.offset.y,
            sprite.hitbox.width,
            sprite.hitbox.height
        )

        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            hitbox,
            1
        )

    def draw_rects(self, sprite):
        rect = pygame.Rect(
            sprite.rect.x - self.offset.x,
            sprite.rect.y - self.offset.y,
            sprite.rect.width,
            sprite.rect.height
        )

        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            rect,
            1
        )

    def update(self):
        "Updates all sprites"
        for sprite in self.sprites():
            sprite.update()