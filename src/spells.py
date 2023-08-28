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

        self.add(self.empty_spell)

    def add(self, *sprites):
        for sprite in sprites:
            super().add(sprite)
            sprite.set_coords(
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
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Empty'
        self.set_animation('spells/empty')

        self.cast_duration = 1000
        self.cost = 0
        self.uses = 1

        self.show_tooltip = False

        # tooltip hover
        self.tooltip_text = Text(self.rect.center, self.game, ())
        self.tooltip_text.set_text(self.name, 20, Color.WHITE)
        self.tooltip_text.draw_background = True

    def kill(self):
        if self.groups():
            spell_group = self.groups()[0]
            spell_group.add(spell_group.empty_spell)

            super().kill()
            del self

            

    def cast(self, coords: list, stats: Stats, target_group):
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
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Earth Shaker'
        self.set_animation('spells/earth_shaker')

        self.cast_duration = 100
        self.cost = 50
        self.uses = 2

        # tooltip hover
        self.tooltip_text = Text(self.rect.center, self.game, ())
        self.tooltip_text.set_text(self.name, 20, Color.WHITE)
        self.tooltip_text.draw_background = True

    def cast(self, coords: list, stats: Stats, target_group):
        '''Creates a projectile at coords'''
        self.uses -= 1

        # creates projectile
        size = (TILE_SIZE * 2,) * 2
        stats = Stats(0, 0, stats.attack * 5, stats.crit_chance, 0)

        explosion = EarthExplosion(coords, size, self.game, self.game.camera_group)
        explosion.set_target(coords, stats, target_group)

        # shakes screen
        self.game.camera_group.screen_shake_offset = -10



        
