import pygame

from libraries.tools import *


class Menu(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = [pygame.display.get_surface().get_height() * 3 / 32] * 2
        menu_width = self.display_surface.get_height() / 3

        self.image = load_image('menu1.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            bottomright=[self.display_surface.get_width(),
                         self.display_surface.get_height()])

        self.menu_rect = pygame.Rect(
            (self.display_surface.get_width() - menu_width) / 2,
            (self.display_surface.get_height() - menu_width) / 2,
            menu_width,
            menu_width)

        # menu text
        self.menu_text, self.menu_text_rect = load_text(
            'Menu',
            (self.menu_rect.centerx, self.menu_rect.top + self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            (50, 50, 50))

        # exit text
        self.draw_exit_text((50, 50, 50))
        self.pressed = False

    def draw_exit_text(self, color):
        self.exit_text, self.exit_text_rect = load_text(
            'Exit',
            (self.menu_rect.centerx, self.menu_rect.bottom - self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            color)
            
    def update(self, game_state):
        pause_left_click = (pygame.mouse.get_pressed()[0]
                            and self.rect.collidepoint(pygame.mouse.get_pos()))

        escape_key = pygame.key.get_pressed()[pygame.K_ESCAPE]

        # checks for left click and escape_key to popup menu
        if (pause_left_click or escape_key) and not self.pressed:
            self.pressed = True
            game_state['paused'] = not game_state['paused']

        elif not (pause_left_click or escape_key) and self.pressed:
            self.pressed = False

        if game_state['paused']:
            self.image = load_image('menu2.png', (self.width, self.height))

            pygame.draw.rect(
                self.display_surface,
                (131, 106, 83),
                self.menu_rect)

            pygame.draw.rect(
                self.display_surface,
                (104, 84, 66),
                self.menu_rect,
                5)

            self.display_surface.blit(self.menu_text, self.menu_text_rect)
            self.display_surface.blit(self.exit_text, self.exit_text_rect)

            if self.exit_text_rect.collidepoint(pygame.mouse.get_pos()):
                self.draw_exit_text((255, 231, 45))
                if pygame.mouse.get_pressed()[0]:
                    game_state['runtime'] = False

            else:
                self.draw_exit_text((50, 50, 50))

        else:
            self.image = load_image('menu1.png', (self.width, self.height))


class Bar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = [pygame.display.get_surface().get_height() / 16] * 2
        self.bar_height = self.display_surface.get_height() / 64
        self.coords = coords

    def draw(self, text):
        pygame.draw.rect(self.display_surface, self.light_color, self.bar, 0)
        pygame.draw.rect(self.display_surface, self.dark_color, self.bar, 3)

        self.display_surface.blit(
            *load_text(
                text,
                self.bar.center,
                self.bar.height,
                (50, 50, 50)))

    def bar_rect(self):
        bar = pygame.Rect(
            self.rect.centerx,
            self.rect.centery - self.bar_height / 2,
            self.rect.width * 1.5,
            self.bar_height)

        return bar

    def set_health(self):
        self.image = load_image('heart.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = self.bar_rect()

        self.light_color = (211, 47, 47)
        self.dark_color = (198, 40, 40)

    def set_speed(self):
        self.image = load_image('lightning.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = self.bar_rect()

        self.light_color = (255, 231, 45)
        self.dark_color = (255, 219, 14)

    def set_attack(self):
        self.image = load_image('sword.png', (self.width, self.height))
        self.rect = self.image.get_rect(
            topleft=self.coords)

        self.bar = self.bar_rect()

        self.light_color = (188, 188, 188)
        self.dark_color = (168, 168, 168)


class TargetBars: 
    def __init__(self, coords: list, groups):
        self.display_surface = pygame.display.get_surface()

        self.coords = pygame.math.Vector2(coords)
        self.width = self.display_surface.get_height() * 9 / 64
        self.height = self.display_surface.get_height() * 11 / 64

        self.health_bar = Bar(
            (self.coords.x,  self.display_surface.get_height()
             * 4 / 128 + self.coords.y),
            groups)

        self.speed_bar = Bar(
            (self.coords.x, self.display_surface.get_height()
             * 9 / 128 + self.coords.y),
            groups)

        self.attack_bar = Bar(
            (self.coords.x, self.display_surface.get_height()
             * 14 / 128 + self.coords.y),
            groups)

        self.bars = [self.health_bar, self.speed_bar, self.attack_bar]

        self.health_bar.set_health()
        self.speed_bar.set_speed()
        self.attack_bar.set_attack()

        self.rect = pygame.Rect(coords, (self.width, self.height))

    def hide_sprites(self):
        for bar in self.bars:
            bar.kill()
            
    def add_sprites(self, group):
        for bar in self.bars:
            group.add(bar)

    def draw(self, target):
        pygame.draw.rect(self.display_surface, (131, 106, 83), self.rect)
        pygame.draw.rect(self.display_surface, (104, 84, 66), self.rect, 5)

        text = [f"{target.health['current']} / {target.health['total']}",
                f"{target.speed['current']}",
                f"{target.attack['current']}"]

        for index, bar in enumerate(self.bars):
            bar.draw(text[index])

        self.display_surface.blit(
            *load_text(
                f'{target.name}',
                (self.coords.x + self.width / 2, self.coords.y +
                 self.display_surface.get_height() * 3 / 128),
                self.display_surface.get_height() / 32,
                (50, 50, 50)))