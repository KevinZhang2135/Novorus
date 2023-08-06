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
        events = [
            event for event in self.game.events
            if event.type == pygame.MOUSEWHEEL
        ]

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


class PlayerHealthBar(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.screen = pygame.display.get_surface()
        self.target = None

        # animation
        self.set_animation('hud/health_bar')

        # health rect
        self.bar_width = self.rect.width * 7 / 8
        self.health_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.bar_width,
            self.rect.height
        )

        self.background_surface = pygame.Surface((
            self.bar_width,
            self.rect.height
        ))

        self.background_surface = color_image(
            self.background_surface,
            Color.CREAM,
            128
        )

        # text
        self.health_text = COMICORO[35].render(str(""), True, Color.BLACK)
        
    def set_target(self, target: pygame.sprite.Sprite):
        self.target = target

    def draw(self):
        text_pos = (
            self.rect.x + self.bar_width / 2 - self.health_text.get_width() / 2,
            self.rect.y + self.rect.height / 2 - self.health_text.get_height() / 2
        )

        self.screen.blit(self.background_surface, self.rect.topleft)
        
        #self.health_text
        pygame.draw.rect(
            self.screen,
            Color.RED,
            self.health_rect
        )

        self.screen.blit(self.image, self.rect.topleft)
        self.screen.blit(self.health_text, text_pos)

    def update(self):
        ratio = self.target.stats.health / self.target.stats.base_health
        if ratio > 1:
            ratio = 1

        self.health_rect.width = self.bar_width * ratio
        self.health_text = COMICORO[35].render(
            str(self.target.stats.health),
            True,
            Color.CREAM
        )


class Cursor(Sprite):
    def __init__(self, size: list, game, groups: pygame.sprite.Group,):
        super().__init__(pygame.mouse.get_pos(), size, game, groups)
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
