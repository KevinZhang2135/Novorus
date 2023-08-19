from constants import *
from sprite import Sprite

import pygame


class Menu(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        self.background_surface = pygame.Surface(self.game.resolution)
        self.background_surface = color_image(
            self.background_surface,
            Color.BLACK,
            128
        )

        # buttons
        pause_button_coords = (
            self.screen.get_width() - HALF_TILE_SIZE,
            self.screen.get_height() - HALF_TILE_SIZE
        )

        self.pause_button = Button(
            pause_button_coords,
            (TILE_SIZE * 1.2,) * 2,
            self.game,
            self,
            optional_key=pygame.K_ESCAPE,
            work_paused=True
        )

        self.pause_button.set_images(
            IMAGES['menu_button'],
            IMAGES['paused']
        )

        # menu rect and surface
        self.menu_rect = pygame.Rect(
            (self.screen.get_width() - TILE_SIZE * 4) / 2,
            (self.screen.get_height() - TILE_SIZE * 4) / 2,
            TILE_SIZE * 4,
            TILE_SIZE * 4
        )

        self.menu_rect_background = pygame.transform.scale(
            IMAGES['menu_box'],
            self.menu_rect.size
        )

        # menu text
        text = COMICORO[50].render('Menu', True, Color.CREAM)
        text_rect = text.get_rect(center=(
            self.screen.get_width() / 2,
            self.screen.get_height() / 2 - 120
        ))

        self.menu_text = text, text_rect

        # exit text
        text = COMICORO[50].render('Exit', True, Color.CREAM)
        text_rect = text.get_rect(center=(
            self.screen.get_width() / 2,
            self.screen.get_height() / 2 + 120
        ))

        # turns yellow upon hover
        self.exit_text = text, text_rect
        self.yellow_exit_text = color_image(
            self.exit_text[0],
            Color.YELLOW
        )

    def menu_popup(self):
        # only displays menu when the game is paused
        if self.pause_button.active:
            self.game.state['unpaused'] = False

            self.screen.blit(self.background_surface, (0, 0))
            self.screen.blit(self.menu_rect_background, self.menu_rect.topleft)
            self.screen.blit(*self.menu_text)

            # exit text turns yellow when hovered upon
            if self.exit_text[1].collidepoint(pygame.mouse.get_pos()):
                self.screen.blit(
                    self.yellow_exit_text,
                    self.exit_text[1]
                )

                # clicking the exit text leaves the game
                if pygame.mouse.get_pressed()[0]:
                    self.game.state['runtime'] = False

            else:
                # exit text when not hovered upon
                self.screen.blit(*self.exit_text)

        else:
            self.game.state['unpaused'] = True

    def render(self):
        for sprite in self.sprites():
            sprite.draw(self.screen)

        self.menu_popup()

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Button(Sprite):
    def __init__(self, coords: list, size: list, game, groups, optional_key=False, work_paused=False):
        super().__init__(coords, size, game, groups)

        self.inactive_sprite = self.active_sprite = self.image

        self.optional_key = optional_key
        self.work_paused = work_paused

        self.pressed = False
        self.active = False

    def set_images(self, inactive_sprite, active_sprite):
        self.inactive_sprite = pygame.transform.scale(
            inactive_sprite,
            self.rect.size
        )

        self.active_sprite = pygame.transform.scale(
            active_sprite,
            self.rect.size
        )

        self.image = self.inactive_sprite

    def press_button(self):
        left_click = (
            pygame.mouse.get_pressed()[0]
            and self.rect.collidepoint(pygame.mouse.get_pos())
        )

        # work_paused determines whether the button is disabled when the game is paused
        button_disabled = not self.game.state['unpaused']
        if self.work_paused:
            button_disabled = False

        key_press = False
        if self.optional_key:
            key_press = pygame.key.get_pressed()[self.optional_key]

        # checks for left click or optional key to popup menu
        if (left_click or key_press) and not self.pressed and not button_disabled:
            self.pressed = True
            self.active = not self.active

        # prevents the button from being held
        elif not (left_click or key_press) and self.pressed and not button_disabled:
            self.pressed = False

        if self.active:
            self.image = self.active_sprite

        else:
            self.image = self.inactive_sprite

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def update(self):
        '''Handles events'''
        self.press_button()


class Cursor(Sprite):
    def __init__(self, size: list, game, groups,):
        super().__init__(pygame.mouse.get_pos(), size, game, groups)
        self.game = game

        # render
        self.sprite_layer = 4

        # animation
        self.set_animation('cursor')

    def offset_mouse_pos(self):
        """Returns the mouse position in relation to the offset screen"""
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += self.game.camera_group.offset.x
        mouse_pos[1] += self.game.camera_group.offset.y

        return mouse_pos

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = list(mouse_pos)

        self.rect.center = mouse_pos


class Text(Sprite):
    def __init__(self, coords: list, game, group):
        super().__init__(coords, (0, 0), game, group)
        self.draw_background = False
        self.background_surface = pygame.Surface(self.size)
        self.background_surface = color_image(
            self.background_surface,
            Color.BLACK,
            128
        )

    def set_text(self, text, font_size, color):
        self.image = COMICORO[font_size].render(text, True, color)
        self.rect = self.image.get_rect(center=self.coords)

        background_size = self.rect.width + 15, self.rect.height + 10
        self.background_surface = pygame.Surface(background_size)
        self.background_surface = color_image(
            self.background_surface,
            Color.BLACK,
            128
        )

    def draw(self, screen):
        if self.draw_background:
            background_coords = tuple(map(
                lambda x: x[0] - x[1] / 2,
                zip(self.rect.center, self.background_surface.get_size())
            ))

            screen.blit(
                self.background_surface,
                background_coords
            )

        screen.blit(
            self.image,
            self.rect.topleft
        )


class PlayerBar(Sprite):
    def __init__(self, coords: list, size: list, game):
        super().__init__(coords, size, game, ())
        self.screen = pygame.display.get_surface()

        # bar rect
        self.bar_color = Color.BLACK
        self.bar_width = self.rect.width
        self.bar_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.bar_width,
            self.rect.height
        )

        # bar background
        self.background_surface = pygame.Surface((
            self.bar_width,
            self.rect.height
        ))

        self.background_surface = color_image(
            self.background_surface,
            Color.BLACK,
            128
        )

        # text
        self.bar_text = COMICORO[35].render(str(""), True, Color.CREAM)

    def render(self):
        text_pos = (
            self.rect.x + self.bar_width / 2 - self.bar_text.get_width() / 2,
            self.rect.y + self.rect.height / 2 - self.bar_text.get_height() / 2
        )

        self.screen.blit(self.background_surface, self.rect.topleft)

        pygame.draw.rect(
            self.screen,
            self.bar_color,
            self.bar_rect
        )

        self.screen.blit(self.image, self.rect.topleft)
        self.screen.blit(self.bar_text, text_pos)

    def update(self):
        pass


class PlayerHealthBar(PlayerBar):
    def __init__(self, coords: list, size: list, game):
        super().__init__(coords, size, game)

        # animation
        self.set_animation('hud/health_bar')

        # bar background
        self.bar_color = Color.RED
        self.bar_width = self.rect.width * 7 / 8

        self.background_surface = pygame.Surface((
            self.bar_width,
            self.rect.height
        ))

        self.background_surface = color_image(
            self.background_surface,
            Color.BLACK,
            128
        )

    def update(self):
        ratio = self.game.player.stats.health / self.game.player.stats.base_health
        if ratio > 1:
            ratio = 1

        self.bar_rect.width = self.bar_width * ratio
        self.bar_text = COMICORO[35].render(
            str(self.game.player.stats.health),
            True,
            Color.CREAM
        )


class PlayerWarmthBar(PlayerBar):
    def __init__(self, coords: list, size: list, game):
        super().__init__(coords, size, game)

        # animation
        self.set_animation('hud/warmth_bar')

        # bar background
        self.bar_color = Color.SKY_BLUE1
        self.bar_width = self.rect.width * 3 / 4

        self.background_surface = pygame.Surface((
            self.bar_width,
            self.rect.height
        ))

        self.background_surface = color_image(
            self.background_surface,
            Color.BLACK,
            128
        )

    def update(self):
        ratio = self.game.player.stats.warmth / self.game.player.stats.base_warmth
        if ratio > 1:
            ratio = 1

        self.bar_rect.width = self.bar_width * ratio
        self.bar_text = COMICORO[35].render(
            str(self.game.player.stats.warmth),
            True,
            Color.CREAM
        )
