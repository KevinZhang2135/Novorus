from constants import *

import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        # camera offset
        self.offset = pygame.math.Vector2()

        # dimensions
        self.half_width = round(self.screen.get_width() / 2)
        self.half_height = round(self.screen.get_height() / 2)

        # lighting
        self.light_colors = (Color.GOLD, Color.SKY_BLUE1, Color.BLACK)
        self.light_sizes = [i for i in range(0, 200, 10)]
        self.lights = {}

        for light_color in self.light_colors:
            self.lights[light_color] = {}

            for light_radius in self.light_sizes:
                image = IMAGES['soft_light'].copy()
                image = color_image(image, light_color, transparency=64)
                image = pygame.transform.scale(
                    image,
                    (light_radius * 2,) * 2
                )

                self.lights[light_color][light_radius] = image

    def center_target(self, target):
        self.offset.xy = -HALF_TILE_SIZE, -HALF_TILE_SIZE

        # stops scrolling screen when the player is past right edge of the screen
        if (target.coords.x >= self.game.level.size.x - self.half_width):
            self.offset.x = self.game.level.size.x \
                - self.screen.get_width() \
                - HALF_TILE_SIZE

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.coords.x > self.half_width):
            self.offset.x = target.coords.x \
                - self.half_width \
                - HALF_TILE_SIZE

        # stops scrolling screen when the player is past bottom edge of the screen
        if (target.coords.y >= self.game.level.size.y - self.half_height - HALF_TILE_SIZE):
            self.offset.y = self.game.level.size.y \
                - self.screen.get_height() \
                - HALF_TILE_SIZE

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.coords.y > self.half_height - HALF_TILE_SIZE):
            self.offset.y = target.coords.y - self.half_height

    def check_bounds(self, sprite: pygame.sprite.Sprite) -> bool:
        # Returns True if sprite is within bounding coords to optimize updates and draws
        topleft_bound = self.offset
        bottomright_bound = self.offset + self.screen.get_size()

        if (sprite.rect.right > topleft_bound.x
                and sprite.rect.left < bottomright_bound.x):
            return True

        elif (sprite.rect.bottom > topleft_bound.y
                and sprite.rect.top < bottomright_bound.y):
            return True

        return False

    def render(self, show_hitboxes=False, show_collision_boxes=False, show_rects=False):
        '''Draws the screen according to player movement'''
        self.center_target(self.game.player)
        self.screen.blit(
            self.game.level.grass_layer,
            (-HALF_TILE_SIZE,) * 2 - self.offset.xy
        )

        self.screen.blit(
            self.game.level.terrain_layer,
            (-HALF_TILE_SIZE,) * 2 - self.offset.xy
        )

        self.screen.blit(
            self.game.level.terrain_overlay_layer,
            (-HALF_TILE_SIZE,) * 2 - self.offset.xy
        )

        # sorts sprites by sprite layer as primary and rectangle bottom as secondary
        for sprite in sorted(
            self.sprites(),
            key=lambda sprite: (
                sprite.sprite_layer,
                sprite.collision_box.bottom
            )
        ):

            # optimizes sprite draws
            if self.check_bounds(sprite):
                # draws shadows
                if sprite.draw_shadow and sprite.shadow:
                    self.draw_shadow(sprite)

                # draws sprite
                offset_pos = sprite.rect.topleft - self.offset
                self.screen.blit(sprite.image, offset_pos)

                # draws lighting
                sprite.draw_light and self.draw_lighting(sprite)

                # draws sprite hitboxes
                show_hitboxes and self.draw_hitboxes(sprite)

                # draws sprite collision boxes
                show_collision_boxes and self.draw_collision_boxes(sprite)

                # draws sprite rects
                show_rects and self.draw_rects(sprite)

    def draw_shadow(self, sprite):
        shadow_pos = sprite.hitbox.bottomleft - self.offset
        shadow_pos.y -= sprite.shadow.surface.get_height()
        self.screen.blit(sprite.shadow.surface, shadow_pos)

    def draw_lighting(self, sprite):
        light = self.lights[sprite.light_color][sprite.light_radius]
        light_pos = (
            sprite.hitbox.centerx - sprite.light_radius,
            sprite.hitbox.centery - sprite.light_radius
        )

        light_pos -= self.offset
        self.screen.blit(light, light_pos)

    def draw_hitboxes(self, sprite):
        hitbox = pygame.Rect(
            sprite.hitbox.x - self.offset.x,
            sprite.hitbox.y - self.offset.y,
            sprite.hitbox.width,
            sprite.hitbox.height
        )

        pygame.draw.rect(
            self.screen,
            Color.RED,
            hitbox,
            1
        )

    def draw_collision_boxes(self, sprite):
        collision_box = pygame.Rect(
            sprite.collision_box.x - self.offset.x,
            sprite.collision_box.y - self.offset.y,
            sprite.collision_box.width,
            sprite.collision_box.height
        )

        pygame.draw.rect(
            self.screen,
            Color.ASH,
            collision_box,
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
            Color.WHITE,
            rect,
            1
        )

    def update(self):
        "Updates all sprites"
        for sprite in self.sprites():
            # optimizes sprite updates
            if self.check_bounds(sprite):
                sprite.update()
