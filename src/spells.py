from constants import *
from sprite import Sprite
from particles import *
from projectiles import *
from ui import Text

import pygame


class SpellGroup(pygame.sprite.GroupSingle):
    def __init__(self, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        self.empty_spell = Spell(
            (0, 0),
            (TILE_SIZE * 1.2,) * 2,
            self.game,
            self
        )

        self.empty_spell.set_animation('spells/empty')

    def add(self, *sprites):
        for sprite in sprites:
            super().add(sprite)
            sprite.set_set_coords(
                self.screen.get_width() - HALF_TILE_SIZE * 5,
                self.screen.get_height() - HALF_TILE_SIZE
            )

    def render(self):
        for sprite in self.sprites():
            sprite.draw(self.screen)

    def update(self):
        for sprite in self.sprites():
            sprite.update()


class Spell(Sprite):
    def __init__(self, coords: list, size: list, game, groups=()):
        super().__init__(coords, size, game, groups)
        self.name = 'Empty'

        self.cast_duration = 1000
        self.cost = 0

        self.show_tooltip = False

        # tooltip hover
        self.tooltip_text = Text(self.rect.center, self.game)
        self.tooltip_text.set_text(self.name, 20, Color.WHITE)
        self.tooltip_text.draw_background = True

    def cast(self, coords: list, stats: Stats):
        '''Creates a projectile at coords'''
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

        # displays tooltip when hovered over
        if self.show_tooltip:
            self.tooltip_text.draw(surface)

    def update(self):
        mouse_coords = list(pygame.mouse.get_pos())
        mouse_coords[0] += 15
        mouse_coords[1] += 10

        self.tooltip_text.rect.topleft = mouse_coords
        self.show_tooltip = self.rect.collidepoint(mouse_coords)


class EarthShaker(Spell):
    def __init__(self, coords: list, size: list, game, groups=()):
        super().__init__(coords, size, game, groups)
        self.name = 'Earth Shaker'

        self.cast_duration = 1000
        self.cost = 50

        self.tooltip_text = Text(self.rect.center, self.game)
        self.tooltip_text.set_text(self.name, 20, Color.WHITE)
        self.tooltip_text.draw_background = True

    def cast(self, coords: list, stats: Stats, group):
        '''Creates a projectile at coords'''
        #Projectile()
        pass
