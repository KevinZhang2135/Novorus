from constants import *

import pygame
import math


class Menu(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game = game

        self.pause_button = Button(
            (self.display_surface.get_width(), self.display_surface.get_height()),
            {'inactive': IMAGES['menu'].copy(),
             'active': IMAGES['paused'].copy()},
            self.game,
            self,
            optional_key=pygame.K_ESCAPE,
            work_paused=True
        )

        menu_width = 360
        menu_height = 360
        self.menu_rect = pygame.Rect(
            (self.display_surface.get_width() - menu_width) / 2,
            (self.display_surface.get_height() - menu_height) / 2,
            menu_width,
            menu_height
        )

        # menu text
        text = COMICORO[50].render('Menu', True, BLACK)
        text_rect = text.get_rect(center=(
            self.display_surface.get_width() / 2,
            self.display_surface.get_height() / 2 - 120
        ))

        self.menu_text = text, text_rect

        # exit text
        text = COMICORO[50].render('Exit', True, BLACK)
        text_rect = text.get_rect(center=(
            self.display_surface.get_width() / 2,
            self.display_surface.get_height() / 2 + 120
        ))

        self.exit_text = text, text_rect
        self.yellow_exit_text = color_image(  # turns yellow upon hover
            self.exit_text[0], YELLOW
        )

    def menu_popup(self):
        # only displays menu when the game is paused
        if self.pause_button.active:
            self.game.state['unpaused'] = False
            pygame.draw.rect(
                self.display_surface,
                BROWN,
                self.menu_rect
            )

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.menu_rect,
                5
            )

            self.display_surface.blit(*self.menu_text)

            # exit text turns yellow when hovered upon
            if self.exit_text[1].collidepoint(pygame.mouse.get_pos()):
                self.display_surface.blit(
                    self.yellow_exit_text,
                    self.exit_text[1]
                )

                # clicking the exit text leaves the game
                if pygame.mouse.get_pressed()[0]:
                    self.game.state['runtime'] = False

            else:
                # exit text when not hovered upon
                self.display_surface.blit(*self.exit_text)

        else:
            self.game.state['unpaused'] = True

    def draw(self):
        for sprite in self.sprites():
            self.display_surface.blit(sprite.image, sprite.rect.topleft)

        self.menu_popup()

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Button(pygame.sprite.Sprite):
    def __init__(self, coords, images: dict, game, groups, optional_key=False, work_paused=False):
        super().__init__(groups)
        self.game = game
        self.width, self.height = 100, 100

        self.sprites = images
        for key, image in images.items():
            self.sprites[key] = pygame.transform.scale(
                image,
                (self.width, self.height)
            )

        self.image = self.sprites['inactive']
        self.rect = self.image.get_rect(bottomright=coords)

        self.optional_key = optional_key
        self.work_paused = work_paused

        self.pressed = False
        self.active = False

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
            self.image = self.sprites['active']

        else:
            self.image = self.sprites['inactive']

    def update(self):
        '''Handles events'''
        self.press_button()


class Inventory(pygame.sprite.Group):
    def __init__(self, items, game):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game = game

        self.inventory_button = Button(
            (self.display_surface.get_width() - 100,
             self.display_surface.get_height()),
            {'inactive': IMAGES['backpack_closed'].copy(
            ), 'active': IMAGES['backpack_opened'].copy()},
            self.game,
            self,
            optional_key=pygame.K_q
        )

        # inventory background
        inventory_width = 400
        inventory_height = 475
        self.inventory_rect = pygame.Rect(
            4,
            (self.display_surface.get_height() - inventory_height) - 4,
            inventory_width,
            inventory_height
        )

        self.inventory_surface = pygame.Surface(
            (self.inventory_rect.width, self.inventory_rect.height))

        # inventory items
        self.items = {}
        for name, tooltip in items.items():
            self.items[name] = Item(name, IMAGES[name], tooltip, 0, self.game)

        self.item_box = IMAGES['item_box']
        self.item_box = pygame.transform.scale(self.item_box, (60, 60))

        # scroll
        self.scroll = 0
        self.scroll_acceleration = 0
        self.scroll_velocity = 0
        self.scroll_max_velocity = 30

    def add_item(self, name, count):
        """Adds items to the inventory, stacking if it is already present"""
        inventory = [item for item in self.sprites()
                     if item != self.inventory_button and item.name == name]

        # if the item already exists in inventory
        if inventory:
            self.items[name].count += count

        # adds a new item into the inventory
        else:
            self.items[name].count = count
            self.add(self.items[name])

    def show_inventory(self):
        """Displays inventory"""
        self.display_surface.blit(
            self.inventory_surface,
            (self.inventory_rect.left, self.inventory_rect.top)
        )

        self.inventory_surface.fill(BROWN)
        pygame.draw.rect(
            self.display_surface,
            DARK_BROWN,
            self.inventory_rect,
            5
        )

        # displays inventory items
        column = 0
        row = 0
        for item in self.sprites():
            if item != self.inventory_button:
                # displays item box
                self.inventory_surface.blit(
                    self.item_box,
                    (
                        column * (self.item_box.get_width() + 15) + 20,
                        row * (self.item_box.get_height() + 15)
                        + 20 - self.scroll
                    )
                )

                # displays item
                item.rect.x = column * (self.item_box.get_width() + 15) + 20
                item.rect.y = row * \
                    (self.item_box.get_height() + 15) + 20 - self.scroll

                self.inventory_surface.blit(
                    item.image,
                    item.rect.topleft
                )

                # show tooltip on hover
                item.show_tooltip()

                # displays item count when the player has multiple copies
                if item.count > 1:
                    text = COMICORO[25].render(str(item.count), True, WHITE)
                    text_rect = text.get_rect(bottomright=(
                        item.rect.right - 5,
                        item.rect.bottom - 5
                    ))

                    self.inventory_surface.blit(text, text_rect)

                column += 1
                if not column % 5 and column != 0:
                    column = 0
                    row += 1

    def scroll_inventory(self):
        """Scrolls the inventory with the mouse wheel"""
        events = pygame.event.get(  # gets a list of filtered events
            eventtype=pygame.MOUSEWHEEL
        )

        # scrolls when mouse is colliding with the inventory
        if self.inventory_rect.collidepoint(pygame.mouse.get_pos()):
            if len(self.sprites()) > 30:
                if events:
                    mousewheel_event = events[0]  # gets mouse wheel event
                    self.scroll_acceleration = self.scroll_max_velocity * \
                        -mousewheel_event.y / abs(mousewheel_event.y)

                    self.scroll_velocity += self.scroll_acceleration
                    self.scroll_velocity *= 0.5

                else:
                    # movement decay when input is not received
                    self.scroll_velocity *= 0.9
                    self.scroll_acceleration = 0

                # movement decay when the speed is low
                if abs(self.scroll_velocity) < 0.1:
                    self.scroll_velocity = 0

                if abs(self.scroll_velocity) < 0.1:
                    self.scroll_velocity = 0

                # scrolls
                self.scroll += self.scroll_velocity

                # prevents scrolling beyond the inventory
                max_scroll = (math.ceil((len(self.sprites()) - 1) / 5) - 6) \
                    * (self.item_box.get_height() + 15)

                if self.scroll < 0:
                    self.scroll = 0

                elif self.scroll > max_scroll:
                    self.scroll = max_scroll

    def draw(self):
        if self.inventory_button.active:
            self.show_inventory()
            self.scroll_inventory()

        self.display_surface.blit(
            self.inventory_button.image,
            self.inventory_button.rect.topleft
        )

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Item(pygame.sprite.Sprite):
    def __init__(self, name, image, tooltip, count, game):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game = game
        self.width, self.height = 60, 60

        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()

        self.name = name
        self.tooltip = tooltip
        self.tooltip[0] = self.tooltip[0]
        self.count = count

        self.tooltip_rect = pygame.Rect(
            self.rect.x, self.rect.y, 100, 10 + 15 * len(self.tooltip))
        self.tooltip_text = []

        # reading tooltip
        for line in tooltip:
            text = COMICORO[20].render(line, True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            self.tooltip_text.append([text, text_rect])

    def show_tooltip(self):
        """Displays tooltip when hovered over"""
        # hard coded fixed margin of 5
        mouse_coords = list(pygame.mouse.get_pos())
        mouse_coords[0] -= 5
        mouse_coords[1] += self.game.player.inventory.inventory_rect.height - \
            self.display_surface.get_height() + 5

        # when mouse is hovered over item
        if self.rect.collidepoint(mouse_coords):
            self.tooltip_rect.topleft = [
                i + 10 for i in pygame.mouse.get_pos()
            ]

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.tooltip_rect
            )

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.tooltip_rect,
                5
            )

            # formatting space between tooltips
            for index, line in enumerate(self.tooltip_text):
                line[1][0] = self.tooltip_rect.topleft[0] + 10
                line[1][1] = self.tooltip_rect.topleft[1] + 15 * index
                self.display_surface.blit(*line)


class Bar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 45, 45
        self.bar_width, self.bar_height = 120, 15

        self.image = pygame.Surface((self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
        self.bar = pygame.Rect(
            self.rect.right,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height
        )

        self.total_bar = self.bar.copy()

        text = COMICORO[20].render(str(""), True, BLACK)
        text_rect = text.get_rect(midleft=self.bar.midleft)
        text_rect.left += self.total_bar.width * 0.25
        self.stat_text = [text, text_rect]


class HealthBar(Bar):
    def __init__(self, coords, groups):
        super().__init__(coords, groups)
        self.image = IMAGES['heart'].copy()
        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

    def draw(self, target):
        pygame.draw.rect(self.display_surface, PECAN, self.total_bar, 2, 3)

        # gets health / total bar ratio
        ratio = target.stats.health / target.stats.base_health
        if ratio > 1:
            ratio = 1

        self.bar.width = self.bar_width * ratio

        # only display the bar when the player has health
        if ratio > 0:
            pygame.draw.rect(self.display_surface, RED, self.bar, 0, 2)
            pygame.draw.rect(self.display_surface, BLOOD_RED, self.bar, 2, 3)

        # displays health text
        self.stat_text[0] = COMICORO[20].render(
            str(target.stats.health),
            True,
            BLACK
        )

        self.display_surface.blit(*self.stat_text)


class SpeedBar(Bar):
    def __init__(self, coords, groups):
        super().__init__(coords, groups)
        self.image = IMAGES['lightning'].copy()
        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

    def draw(self, target):
        pygame.draw.rect(self.display_surface, YELLOW, self.bar, 0, 3)
        pygame.draw.rect(self.display_surface, GOLD, self.bar, 2, 3)

        # displays speed text
        self.stat_text[0] = COMICORO[20].render(
            str(target.stats.speed),
            True,
            BLACK
        )

        self.display_surface.blit(*self.stat_text)


class AttackBar(Bar):
    def __init__(self, coords, groups):
        super().__init__(coords, groups)
        self.image = IMAGES['sword'].copy()
        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

    def draw(self, target):
        pygame.draw.rect(self.display_surface, GREY, self.bar, 0, 3)
        pygame.draw.rect(self.display_surface, DARK_GREY, self.bar, 2, 3)

        # displays attack text
        self.stat_text[0] = COMICORO[20].render(
            str(target.stats.attack),
            True,
            BLACK
        )

        self.display_surface.blit(*self.stat_text)


class BarGroup(pygame.sprite.Group):
    def __init__(self, coords, game):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game = game
        self.coords = pygame.math.Vector2(coords)

        # margins between bars
        padding = 40
        self.padding_step = 30
        for bar in (HealthBar, SpeedBar, AttackBar):
            bar = bar(
                (self.coords[0], self.coords[1] + padding),
                self
            )

            padding += self.padding_step

        self.width = bar.bar.right + 10
        self.height = bar.rect.top - self.coords.y + 50

        self.rect = pygame.Rect(self.coords, (self.width, self.height))
        self.exp_rect = pygame.Rect(self.coords, (60, 30))

        name_text = COMICORO[25].render('', True, BLACK)
        name_text_rect = name_text.get_rect(center=(
            self.coords.x + self.width / 4,
            self.coords.y + self.padding_step
        ))

        self.name_text = [name_text, name_text_rect]

        exp_text = COMICORO[25].render('', True, BLACK)
        exp_text_rect = exp_text.get_rect(center=self.exp_rect.center)

        self.exp_text = [exp_text, exp_text_rect]

    def draw(self, targets, always_show=False):
        target = None
        if (always_show):
            # selects the first sprite
            target = targets.sprites()[0]

        else:
            for target in targets:
                if (target.in_combat or target.rect.collidepoint(self.game.cursor.offset_mouse_pos())):
                    break

                target = None

        # draws the card of the target's health, speed, and attack
        if target and target.show_stats:
            pygame.draw.rect(self.display_surface, BROWN, self.rect, 0, 3)
            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN, 
                self.rect, 
                3, 
                3
            )

            # displays target level
            self.name_text[0] = COMICORO[25].render(
                f'{target.name}', 
                True, 
                BLACK
            )

            self.display_surface.blit(*self.name_text)

            # blits the bar
            for sprite in self.sprites():
                self.display_surface.blit(
                    sprite.image, 
                    sprite.rect.topleft
                )

                sprite.draw(target)

            # displays exp if the cursor is hovered over the name
            if self.name_text[1].collidepoint(pygame.mouse.get_pos()):
                text = f'exp {target.exp}'
                if target.exp_levels:
                    text += f' / {target.exp_levels[target.level - 1]}'

                self.exp_text[0] = COMICORO[25].render(text, True, BLACK)
                self.exp_text[1] = self.exp_text[0].get_rect(
                    center=self.exp_rect.center)

                self.exp_rect.width = self.exp_text[1].width + 20
                self.exp_rect.topleft = pygame.mouse.get_pos()

                pygame.draw.rect(
                    self.display_surface,
                    BROWN, 
                    self.exp_rect
                )

                pygame.draw.rect(
                    self.display_surface,
                    DARK_BROWN, 
                    self.exp_rect, 
                    3
                )

                self.display_surface.blit(*self.exp_text)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, tile_size, game, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        self.game = game
        self.tile_size = tile_size

        self.image = IMAGES['cursor'].copy()
        self.image = pygame.transform.scale(self.image, (100, 100))

        self.rect = self.image.get_rect(center=(0, 0))

        self.sprite_layer = 4

    def offset_mouse_pos(self):
        """Returns the mouse position in relation to the offset screen"""
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += self.game.camera_group.offset.x
        mouse_pos[1] += self.game.camera_group.offset.y

        return mouse_pos

    def update(self):
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] = round(mouse_pos[0] / TILE_SIZE) * TILE_SIZE
        mouse_pos[1] = round(mouse_pos[1] / TILE_SIZE) * TILE_SIZE

        self.rect.center = mouse_pos
