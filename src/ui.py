from constants import *
from color import Color
from sprite import Sprite

import pygame


class Menu(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        self.pause_button = Button(
            self.screen.get_size(),
            (120, 120),
            self.game,
            self,
            optional_key=pygame.K_ESCAPE,
            work_paused=True
        )

        self.pause_button.set_images(
            IMAGES['menu'],
            IMAGES['paused']
        )

        menu_width = 360
        menu_height = 360
        self.menu_rect = pygame.Rect(
            (self.screen.get_width() - menu_width) / 2,
            (self.screen.get_height() - menu_height) / 2,
            menu_width,
            menu_height
        )

        # menu text
        text = COMICORO[50].render('Menu', True, Color.BLACK)
        text_rect = text.get_rect(
            center=(
                self.screen.get_width() / 2,
                self.screen.get_height() / 2 - 120
            )
        )

        self.menu_text = text, text_rect

        # exit text
        text = COMICORO[50].render('Exit', True, Color.BLACK)
        text_rect = text.get_rect(
            center=(
                self.screen.get_width() / 2,
                self.screen.get_height() / 2 + 120
            )
        )

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
            pygame.draw.rect(
                self.screen,
                Color.BROWN,
                self.menu_rect
            )

            pygame.draw.rect(
                self.screen,
                Color.DARK_BROWN,
                self.menu_rect,
                5
            )

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

    def draw(self):
        for sprite in self.sprites():
            self.screen.blit(sprite.image, sprite.rect.topleft)

        self.menu_popup()

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Button(Sprite):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group, optional_key=False, work_paused=False):
        super().__init__(coords, size, game, groups)
        self.set_coords(
            self.coords.x - self.rect.width / 2,
            self.coords.y - self.rect.height / 2
        )

        self.inactive_sprite = self.active_sprite = self.image

        self.optional_key = optional_key
        self.work_paused = work_paused

        self.pressed = False
        self.active = False

    def set_images(self, inactive_sprite, active_sprite):
        self.inactive_sprite = pygame.transform.scale(
            inactive_sprite, self.rect.size)
        self.active_sprite = pygame.transform.scale(
            active_sprite, self.rect.size)
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

    def update(self):
        '''Handles events'''
        self.press_button()


class Inventory(pygame.sprite.Group):
    def __init__(self, items: dict, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        self.inventory_button = Button(
            (
                self.screen.get_width() - 90,
                self.screen.get_height()
            ),
            (120, 120),
            self.game,
            self,
            optional_key=pygame.K_q
        )

        self.inventory_button.set_images(
            IMAGES['backpack_closed'],
            IMAGES['backpack_opened']
        )

        # inventory background
        inventory_width = 400
        inventory_height = 475
        self.inventory_rect = pygame.Rect(
            4,
            (self.screen.get_height() - inventory_height) - 4,
            inventory_width,
            inventory_height
        )

        self.inventory_surface = pygame.Surface(
            (self.inventory_rect.width, self.inventory_rect.height)
        )

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

    def add_item(self, name: str, count: int):
        """Adds items to the inventory, stacking if it is already present"""
        inventory = [
            item for item in self.sprites()
            if item != self.inventory_button and item.name == name
        ]

        # if the item already exists in inventory
        if inventory:
            self.items[name].count += count

        # adds a new item into the inventory
        else:
            self.items[name].count = count
            self.add(self.items[name])

    def show_inventory(self):
        """Displays inventory"""
        self.screen.blit(
            self.inventory_surface,
            (self.inventory_rect.left, self.inventory_rect.top)
        )

        self.inventory_surface.fill(Color.BROWN)
        pygame.draw.rect(
            self.screen,
            Color.DARK_BROWN,
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
                item.rect.y = row * (self.item_box.get_height() + 15) \
                    + 20 \
                    - self.scroll

                self.inventory_surface.blit(
                    item.image,
                    item.rect.topleft
                )

                # show tooltip on hover
                item.show_tooltip()

                # displays item count when the player has multiple copies
                if item.count > 1:
                    text = COMICORO[25].render(
                        str(item.count),
                        True,
                        Color.WHITE
                    )

                    text_rect = text.get_rect(
                        bottomright=(
                            item.rect.right - 5,
                            item.rect.bottom - 5
                        )
                    )

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
                    self.scroll_acceleration = self.scroll_max_velocity \
                        * -mousewheel_event.y \
                        / abs(mousewheel_event.y)
                    

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
                max_scroll = ((math.ceil((len(self.sprites()) - 1) / 5) - 6) \
                    * (self.item_box.get_height() + 15))

                if self.scroll < 0:
                    self.scroll = 0

                elif self.scroll > max_scroll:
                    self.scroll = max_scroll

    def draw(self):
        if self.inventory_button.active:
            self.show_inventory()
            self.scroll_inventory()

        self.screen.blit(
            self.inventory_button.image,
            self.inventory_button.rect.topleft
        )

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Item(pygame.sprite.Sprite):
    def __init__(self, name: str, image: pygame.Surface, tooltip: str, count: int, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
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
            text = COMICORO[20].render(line, True, Color.WHITE)
            text_rect = text.get_rect(center=self.rect.center)
            self.tooltip_text.append([text, text_rect])

    def show_tooltip(self):
        """Displays tooltip when hovered over"""
        # hard coded fixed margin of 5
        mouse_coords = list(pygame.mouse.get_pos())
        mouse_coords[0] -= 5
        mouse_coords[1] += self.game.player.inventory.inventory_rect.height - \
            self.screen.get_height() + 5

        # when mouse is hovered over item
        if self.rect.collidepoint(mouse_coords):
            self.tooltip_rect.topleft = [
                i + 10 for i in pygame.mouse.get_pos()
            ]

            pygame.draw.rect(
                self.screen,
                Color.DARK_BROWN,
                self.tooltip_rect
            )

            pygame.draw.rect(
                self.screen,
                Color.DARK_BROWN,
                self.tooltip_rect,
                5
            )

            # formatting space between tooltips
            for index, line in enumerate(self.tooltip_text):
                line[1][0] = self.tooltip_rect.topleft[0] + 10
                line[1][1] = self.tooltip_rect.topleft[1] + 15 * index
                self.screen.blit(*line)


class Bar(pygame.sprite.Sprite):
    def __init__(self, coords: list, groups: pygame.sprite.Group):
        super().__init__(groups)
        self.screen = pygame.display.get_surface()

        # images and rects
        self.width, self.height = 45, 45
        self.bar_width, self.bar_height = 150, 15

        self.image = pygame.Surface((self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)

        # bar rect
        self.bar = pygame.Rect(
            self.rect.right,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height
        )

        self.total_bar = self.bar.copy()

        # bar text
        text = COMICORO[20].render(str(""), True, Color.BLACK)
        text_rect = text.get_rect(midleft=self.bar.midleft)
        text_rect.left += self.total_bar.width * 0.25
        self.stat_text = [text, text_rect]


class HealthBar(Bar):
    def __init__(self, coords: list, groups: pygame.sprite.Group):
        super().__init__(coords, groups)
        self.image = IMAGES['heart'].copy()
        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

    def draw(self, target: pygame.sprite.Sprite):
        pygame.draw.rect(
            self.screen,
            Color.PECAN,
            self.total_bar,
            2,
            self.bar.height // 2
        )

        # gets health / total bar ratio
        ratio = target.stats.health / target.stats.base_health
        if ratio > 1:
            ratio = 1

        self.bar.width = self.bar_width * ratio

        # only display the bar when the player has health
        if ratio > 0:
            pygame.draw.rect(
                self.screen,
                Color.RED,
                self.bar,
                0,
                self.bar.height // 2
            )

            pygame.draw.rect(
                self.screen,
                Color.BLOOD_RED,
                self.bar,
                2,
                self.bar.height // 2
            )

        # displays health text
        self.stat_text[0] = COMICORO[20].render(
            str(target.stats.health),
            True,
            Color.BLACK
        )

        self.screen.blit(*self.stat_text)


class SpeedBar(Bar):
    def __init__(self, coords: list, groups: pygame.sprite.Group):
        super().__init__(coords, groups)
        self.image = IMAGES['boots'].copy()
        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

    def draw(self, target):
        pygame.draw.rect(
            self.screen,
            Color.YELLOW,
            self.bar,
            0,
            self.bar.height // 2
        )

        pygame.draw.rect(
            self.screen,
            Color.GOLD,
            self.bar,
            2,
            self.bar.height // 2
        )

        # displays speed text
        self.stat_text[0] = COMICORO[20].render(
            str(target.stats.speed),
            True,
            Color.BLACK
        )

        self.screen.blit(*self.stat_text)


class AttackBar(Bar):
    def __init__(self, coords: list, groups: pygame.sprite.Group):
        super().__init__(coords, groups)
        self.image = IMAGES['sword'].copy()
        self.image = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )

    def draw(self, target):
        pygame.draw.rect(
            self.screen,
            Color.GREY,
            self.bar,
            0,
            self.bar.height // 2
        )

        pygame.draw.rect(
            self.screen,
            Color.DARK_GREY,
            self.bar,
            2,
            self.bar.height // 2
        )

        # displays attack text
        self.stat_text[0] = COMICORO[20].render(
            str(target.stats.attack),
            True,
            Color.BLACK
        )

        self.screen.blit(*self.stat_text)


class BarGroup(pygame.sprite.Group):
    def __init__(self, coords: list, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
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

        # rects
        self.width = bar.bar.right + 20
        self.height = bar.rect.top - self.coords.y + 50

        self.rect = pygame.Rect(self.coords, (self.width, self.height))

        # name text
        name_text = COMICORO[25].render('', True, Color.BLACK)
        name_text_rect = name_text.get_rect(
            center=(
                self.coords.x + self.width / 4,
                self.coords.y + self.padding_step
            )
        )

        self.name_text = [name_text, name_text_rect]

    def draw(self, targets: pygame.sprite.Group, always_show: bool = False):
        target = None
        if (always_show):
            # selects the first sprite
            target = targets.sprites()[0]

        else:
            for target in targets:
                if (target.hitbox.collidepoint(self.game.cursor.offset_mouse_pos())):
                    break

                target = None

        # draws the card of the target's health, speed, and attack
        if target and target.show_stats:
            pygame.draw.rect(self.screen, Color.BROWN, self.rect)
            pygame.draw.rect(
                self.screen,
                Color.DARK_BROWN,
                self.rect,
                3,
            )

            # displays target name
            self.name_text[0] = COMICORO[25].render(
                f'{target.name}',
                True,
                Color.BLACK
            )

            self.screen.blit(*self.name_text)

            # blits the bar
            for sprite in self.sprites():
                self.screen.blit(
                    sprite.image,
                    sprite.rect.topleft
                )

                sprite.draw(target)


class Cursor(Sprite):
    def __init__(self, size: list, game, groups: pygame.sprite.Group,):
        super().__init__(pygame.mouse.get_pos(), size, game, groups)
        self.screen = pygame.display.get_surface()
        self.game = game

        # render
        self.sprite_layer = 4

        # images and rects
        self.image = IMAGES['cursor'].copy()
        self.image = pygame.transform.scale(self.image, size)

        self.rect = self.image.get_rect(center=(0, 0))

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
