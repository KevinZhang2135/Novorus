from constants import *
from sprite import Sprite
from ui import Button

import pygame


class Inventory(pygame.sprite.Group):
    def __init__(self, coords: list, items: dict, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        self.ITEM_WIDTH = 60
        self.MARGIN = 30
        self.HALF_MARGIN = self.MARGIN / 2
        self.PADDING = 5

        self.INVENTORY_RECT_WIDTH = TILE_SIZE * 4
        self.INVENTORY_SURFACE_WIDTH = self.INVENTORY_RECT_WIDTH - self.MARGIN * 2

        self.MAX_ROWS = 5
        self.MAX_COLUMNS = 5
        self.ROW_MARGIN = (self.INVENTORY_SURFACE_WIDTH - self.MAX_ROWS * self.ITEM_WIDTH) \
            / (self.MAX_ROWS - 1)

        self.coords = pygame.math.Vector2(*coords)

        # buttons
        inventory_button_coords = (
            self.game.width - HALF_TILE_SIZE * 3,
            self.game.height - HALF_TILE_SIZE
        )

        self.inventory_button = Button(
            inventory_button_coords,
            (TILE_SIZE * 1.2,) * 2,
            self.game,
            self,
            optional_key=pygame.K_q
        )

        self.inventory_button.set_images(
            IMAGES['backpack_closed'],
            IMAGES['backpack_opened']
        )

        # inventory rect and surface
        self.inventory_rect = pygame.Rect(
            self.coords.x,
            self.coords.y,
            self.INVENTORY_RECT_WIDTH,
            self.INVENTORY_RECT_WIDTH
        )

        self.inventory_rect_background = pygame.transform.scale(
            IMAGES['inventory_box'],
            self.inventory_rect.size
        )

        # inventory surface
        self.inventory_surface = []
        self.inventory_surface.append(
            pygame.Surface(
                (self.INVENTORY_SURFACE_WIDTH,) * 2,
                flags=pygame.SRCALPHA
            )
        )

        # inventory surface coords
        self.inventory_surface.append(tuple(map(
            lambda x: x + self.MARGIN,
            self.inventory_rect.topleft
        )))

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
        self.scroll_max_velocity = 8

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
            self.inventory_rect_background,
            self.inventory_rect.topleft
        )

        self.screen.blit(*self.inventory_surface)
        self.inventory_surface[0].fill((0, 0, 0, 0))

        # displays inventory items
        row, column = 0, 0
        for item in self.sprites():
            if item != self.inventory_button:
                # determines position by column as x and row as y
                item_pos = [
                    column * self.item_box.get_width(),
                    row * self.item_box.get_height()
                    - self.scroll
                ]

                # inserts margins
                item_pos[0] += (column) * (self.ROW_MARGIN)
                item_pos[1] += (row) * (self.ROW_MARGIN)

                self.inventory_surface[0].blit(
                    self.item_box,
                    item_pos
                )

                # displays item
                item.rect.x, item.rect.y = item_pos
                self.inventory_surface[0].blit(
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
                        Color.BLACK
                    )

                    text_rect = text.get_rect(bottomright=(
                        item.rect.right - self.MARGIN // 3,
                        item.rect.bottom - self.MARGIN // 3
                    ))

                    self.inventory_surface[0].blit(text, text_rect)

                column += 1
                if not column % self.MAX_COLUMNS and column != 0:
                    column = 0
                    row += 1

    def scroll_inventory(self):
        """Scrolls the inventory with the mouse wheel"""
        events = [
            event for event in self.game.events
            if event.type == pygame.MOUSEWHEEL
        ]

        # does not check scroll unless mouse is hovering above inventory
        if not self.inventory_rect.collidepoint(pygame.mouse.get_pos()):
            return

        # does not check scroll unless item count exceeds threshold
        # removes the inventory button icon
        num_items = len(self.sprites()) - 1
        item_threshold = self.MAX_ROWS * self.MAX_COLUMNS
        if not num_items > item_threshold:
            return

        # scrolls when mouse is colliding with the inventory
        # enables scroll when items exceeds maximum amount dsiplayed
        if events:
            mousewheel_event = events[0]  # gets mouse wheel event
            self.scroll_acceleration = -self.scroll_max_velocity
            if mousewheel_event.y < 0:
                self.scroll_acceleration *= -1

            self.scroll_velocity += self.scroll_acceleration
            self.scroll_velocity *= 0.5

        else:
            # movement decay when input is not received
            self.scroll_velocity *= 0.95
            self.scroll_acceleration = 0

        # movement decay when the speed is low
        if abs(self.scroll_velocity) < 0.05:
            self.scroll_velocity = 0

        if abs(self.scroll_velocity) < 0.05:
            self.scroll_velocity = 0

        # scrolls
        self.scroll += self.scroll_velocity

        # prevents scrolling beyond the inventory
        max_scroll = (math.ceil(num_items / self.MAX_COLUMNS)) \
            * (self.ITEM_WIDTH + self.ROW_MARGIN) \
            - self.ROW_MARGIN - self.INVENTORY_SURFACE_WIDTH

        if self.scroll < 0:
            self.scroll = 0

        elif self.scroll > max_scroll:
            self.scroll = max_scroll

    def render(self):
        if self.inventory_button.active:
            self.show_inventory()
            self.scroll_inventory()

        self.inventory_button.draw(self.screen)

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Item(Sprite):
    def __init__(self, name: str, image: pygame.Surface, tooltip: list, count: int, game):
        super().__init__((0, 0), (60, 60), game, ())
        # defaults width and height to 60

        self.screen = pygame.display.get_surface()
        self.game = game

        self.TOOLTIP_MARGIN = 10
        self.TOOLTIP_LENGTH = 15

        self.name = name
        self.tooltip = tooltip
        self.count = count

        self.image = pygame.transform.scale(image, self.size)
        self.tooltip_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            TILE_SIZE,
            self.TOOLTIP_MARGIN + self.TOOLTIP_LENGTH * len(self.tooltip)
        )

        self.tooltip_text = []

        # reading tooltip
        for line in tooltip:
            text = COMICORO[20].render(line, True, Color.WHITE)
            text_rect = text.get_rect(center=self.rect.center)
            self.tooltip_text.append([text, text_rect])

    def show_tooltip(self):
        """Displays tooltip when hovered over"""
        player_inventory = self.game.player.inventory

        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += -player_inventory.MARGIN
        mouse_pos[1] += -player_inventory.MARGIN - player_inventory.coords.y

        # y distance of "hoverable" inventory
        hover_height = player_inventory.INVENTORY_RECT_WIDTH \
            - 2 * player_inventory.MARGIN

        # when mouse is hovered over item
        if (mouse_pos[1] < hover_height
                and self.rect.collidepoint(mouse_pos)):

            self.tooltip_rect.topleft = list(map(
                lambda x: x + self.TOOLTIP_MARGIN,
                pygame.mouse.get_pos()
            ))

            pygame.draw.rect(
                self.screen,
                Color.DARK_BROWN,
                self.tooltip_rect
            )

            # formatting space between tooltips
            for index, line in enumerate(self.tooltip_text):
                line[1][0] = self.tooltip_rect.topleft[0] + 10
                line[1][1] = self.tooltip_rect.topleft[1] + 15 * index
                self.screen.blit(*line)
