from tkinter import Y
import pygame
import random
import os
import csv
import math


class Level:
    def __init__(self, floor_level, tile_size):
        global player

        self.size = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.tile_size = tile_size
        self._floor_level = floor_level
        self.display_surface = pygame.display.get_surface()

        self.level_updated = False
        self.transitioning = False
        self.level_transition_rect = pygame.Rect(
            -self.display_surface.get_width(),
            0,
            self.display_surface.get_width(),
            self.display_surface.get_height())

        text = COMICORO[50].render(f'Floor {self.floor_level}', True, BLACK)
        text_rect = text.get_rect(
            center=(self.display_surface.get_width() / 2, 
                    self.display_surface.get_height() - 50))

        self.floor_level_text = [text, text_rect]
        self.read_csv_level()
        self.update_lighting()

    @property
    def floor_level(self):
        return self._floor_level

    @floor_level.setter
    def floor_level(self, value):
        self._floor_level = value
        self.transitioning = True
    
    def transition_level(self):
        global player

        if self.transitioning:
            self.level_transition_rect.x += 75
            if (self.level_transition_rect.x > 0
                and not self.level_updated):
                self.level_updated = True
                
                self.clear_level()
                self.read_csv_level()
                self.update_lighting()

                text = COMICORO[50].render(f'Floor {self.floor_level}', True, BLACK)

                self.floor_level_text[0] = text

                player.velocity.x = 0
                player.velocity.y = 0

            if self.level_transition_rect.x > self.display_surface.get_width():
                self.level_transition_rect.x = -self.display_surface.get_width()

                self.transitioning = False
                self.level_updated = False

    def read_csv_level(self):
        files = os.listdir(f'./levels/{self._floor_level}')

        i = 0
        for path in files:
            file_extention = os.path.splitext(path)[1]
            if file_extention != '.csv':
                raise Exception(f'File "{path}" is not recognized as a csv file.')

            with open(os.path.join(f'./levels/{self._floor_level}', path)) as file:
                csv_file = list(csv.reader(file))
                self.create_tile_group(csv_file, path)
                if not i: # determines the dimensions of the first csv_file
                    self.size.x = len(list(csv_file)[0]) * self.tile_size
                    self.size.y = len(list(csv_file)) * self.tile_size

                    self.rect = pygame.Rect(0, 0, *self.size)
                    i += 1
            
    def clear_level(self):
        global camera_group, player_group

        for sprite in camera_group.sprites():
            if sprite not in player_group:
                sprite.kill()
                del sprite

    def update_lighting(self):
        global light_group
        if self.floor_level > 1:
            light_group.color = MIDNIGHT

    def create_tile_group(self, csv_file, path):
        create_tile = {'player': self.set_player_coords,
                       'terrain': self.add_terrain,
                       'wall': self.add_walls,
                       'enemies': self.add_enemies,
                       'chest': self.add_chests,
                       'static_decor': self.add_static_decor,
                       'animated_decor': self.add_animated_decor,
                       'exit': self.add_exit}

        if path[:-4] not in create_tile:
            raise Exception(f'The csv file "{path}" is invalid.')

        for row_index, row in enumerate(csv_file):
            for col_index, id in enumerate(row):
                id = int(id)
                if id != -1 and id >= 0:
                    x = col_index * self.tile_size
                    y = row_index * self.tile_size
                    create_tile[path[:-4]](id, (x, y))

                else:
                    if id < -1:
                        raise Exception(f'Unexpected value was found in csv file "{path}".')
                    
    def set_player_coords(self, id, coords):
        global player

        player.rect.center = coords
        player.coords = player.rect.center

    def add_terrain(self, id, coords):
        sprites = ('path1',
                   'path2',
                   'path3',
                   'path4',
                   'path5',
                   'path6',
                   'path7',
                   'path8',
                   'path9',
                   'path10',
                   'grassy1',
                   'grassy2',
                   'path11',
                   'path12',
                   'path13',
                   'path14',
                   'path15',
                   'path16',
                   'path17',
                   'path18',
                   'path19',
                   'path20',
                   'path21',
                   'path22',
                   'path23',
                   'path24',
                   'path25',
                   'path26',
                   'path27',
                   'path28',
                   'path29',
                   'path30',
                   'path31',
                   'grassy3',
                   'grassy4',
                   'grassy5',
                   'grassy6',
                   )

        size = (100,) * 2
        terrain_tile = StaticTile(
            coords,
            size,
            sprites[id],
            camera_group)

        terrain_tile.sprite_layer = -1
        
    def add_walls(self, id, coords):
        global camera_group, collision_group

        images = ('brick_top',
                  'brick_middle',
                  'brick_bottom',
                  'brick_pile',
                  'brick_side')

        wall = StaticTile(
            coords,
            (100, 100),
            images[id],
            (camera_group, collision_group))

    def add_enemies(self, id, coords):
        global camera_group, enemy_group, light_group

        enemies = (Ghost,
                   Mimic,
                   Sunflower)

        sprite_size = (50, 60, 30)

        enemy = enemies[id](coords, [sprite_size[id]] * 2,
                            self.floor_level, (camera_group, enemy_group))
        enemy.rect.centerx += random.randint(-25, 25)
        enemy.rect.centery += random.randint(-25, 25)

    def add_chests(self, id, coords):
        global camera_group, collision_group

        chest = Chest(
            coords,
            (60, 60),
            (camera_group, collision_group))

    def add_static_decor(self, id, coords):
        global camera_group

        sprites = ({'file': 'grass1',
                    'size': 30},

                   {'file': 'grass2',
                    'size': 30},

                   {'file': 'grass3',
                    'size': 30},

                   {'file': 'rock1',
                    'size': 50},

                   {'file': 'rock2',
                    'size': 40},

                   {'file': 'rock3',
                    'size': 50},

                   {'file': 'rock4',
                    'size': 50},

                   {'file': 'tree1',
                    'size': 120},

                   {'file': 'tree2',
                    'size': 120},

                   {'file': 'tree3',
                    'size': 120},

                   {'file': 'tree4',
                    'size': 30})

        size = round(randomize(sprites[id]['size'], 0.1))
        decor = StaticTile(
            coords,
            [size] * 2,
            sprites[id]['file'],
            camera_group)

        decor.rect.centerx += random.randint(-25, 25)
        decor.rect.centery += random.randint(-25, 25)

        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

    def add_animated_decor(self, id, coords):
        global camera_group, light_group

        decor_sprites = (Torch,)
        sprite_size = (50,)
        size = round(randomize(sprite_size[id], 0.1))

        decor = decor_sprites[id](
            coords,
            [size] * 2,
            (camera_group, light_group))
        
        decor.sprite_layer = 2

    def add_exit(self, id, coords):
        global camera_group

        exit = LevelExit(
            coords, [round(self.tile_size * 0.8)] * 2, camera_group)

    def draw(self):
        self.display_surface.blit(*self.floor_level_text)

        if self.transitioning:
            pygame.draw.rect(
                self.display_surface,
                BLACK,
                self.level_transition_rect)
            
    def update(self):
        """Handles events"""
        self.transition_level()
        

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2

        self.texts = []

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def custom_draw(self, player, show_hitboxes=False):
        '''Draws the screen according to player movement'''
        self.center_target(player)
        # sorts sprites by sprite layer as primary and rectangle bottom as secondary
        for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.sprite_layer, sprite.rect.bottom)):
            if (abs(player.rect.centerx
                    - sprite.rect.centerx 
                    + sprite.rect.width / 2) < self.half_width
    
                or abs(player.rect.centery
                       - sprite.rect.centery 
                       + sprite.rect.height / 2) < self.half_height):
                       
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

                if show_hitboxes:
                    hitbox = pygame.Rect(
                        sprite.rect.x - self.offset.x,
                        sprite.rect.y - self.offset.y,
                        sprite.rect.width,
                        sprite.rect.height)

                    pygame.draw.rect(
                        self.display_surface,
                        (255, 0, 0),
                        hitbox,
                        1)

        expired_texts = []
        for index, text in enumerate(self.texts):
            if text.alpha <= 0:
                expired_texts.append(index)

            text.update()
            offset_pos = text.rect.topleft - self.offset
            self.display_surface.blit(text.text, offset_pos)

        # removes texts that have expired
        expired_texts.sort(reverse=True)
        for index in expired_texts:
            expired_text = self.texts.pop(index)
            del expired_text

    def update(self):
        "Updates all sprites"
        global player

        for sprite in self.sprites():
            if (abs(player.rect.centerx
                    - sprite.rect.centerx 
                    + sprite.rect.width / 2) < self.half_width
    
                or abs(player.rect.centery
                       - sprite.rect.centery 
                       + sprite.rect.height / 2) < self.half_height):

                sprite.update()


class TextPopUp:
    def __init__(self, text, rect):
        self.text = text
        self.rect = rect

        self.alpha = 255

        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)

        self.time = pygame.time.get_ticks()
        self.expiration_time = randomize(1000, 0.1)

    def movement(self):
        '''Moves the text vertically'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        # movement decay when the speed is low
        if abs(self.velocity.x) < 0.25:
            self.velocity.x = 0

        if abs(self.velocity.y) < 0.25:
            self.velocity.y = 0

        self.rect.center += self.velocity

    def expire(self):
        '''Fades text after its expiration time'''
        if pygame.time.get_ticks() - self.time > self.expiration_time:
            self.alpha -= 10
            if self.alpha > 0:
                self.text.set_alpha(self.alpha)

    def update(self):
        '''Handles events'''
        self.movement()
        self.expire()


class Particle(pygame.sprite.Sprite):
    def __init__(self, coords, size, image, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.alpha = 255
        self.image = IMAGES[image].copy()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)

        self.time = pygame.time.get_ticks()
        self.expiration_time = randomize(1000, 0.1)

        self.sprite_layer = 3

    def movement(self):
        '''Handles movement'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        # movement decay when the speed is low
        if abs(self.velocity.x) < 0.25:
            self.velocity.x = 0

        if abs(self.velocity.y) < 0.25:
            self.velocity.y = 0

        self.rect.center += self.velocity

    def expire(self):
        '''Deletes particle after its expiration time'''
        if pygame.time.get_ticks() - self.time > self.expiration_time:
            self.alpha -= 10
            if self.alpha > 0:
                self.image.set_alpha(self.alpha)
                
            else:
                self.kill()
                del self
                                 
    def update(self):
        '''Handles events'''
        self.movement()
        self.expire()


class LightSources(pygame.sprite.Group):
    def __init__(self, resolution):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2
        self.resolution = resolution

        self.filter = pygame.surface.Surface(self.resolution)

        # light offset
        self.offset = pygame.math.Vector2()
        self.sprite_layer = 3
        self.color = LIGHT_GREY

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def render_lighting(self, player):
        self.filter.fill(self.color)
        self.center_target(player)
        for sprite in self.sprites():
            if (abs(player.rect.left - sprite.rect.left) < self.half_width
                or abs(player.rect.top - sprite.rect.top) < self.half_height):
                offset_pos = sprite.rect.topleft \
                            - self.offset \
                            + list(map(lambda x: x / 2, sprite.rect.size)) \
                            - sprite.light_size / 2
                            
                self.filter.blit(sprite.light, offset_pos)

        self.display_surface.blit(
            self.filter,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)


class Menu(pygame.sprite.Group):
    def __init__(self):
        global game_state

        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.pause_button = Button(
            (self.display_surface.get_width(), self.display_surface.get_height()),
            {'inactive': IMAGES['menu'].copy(), 'active': IMAGES['paused'].copy()},
            self,
            optional_key=pygame.K_ESCAPE,
            work_paused = True)

        menu_width = 360
        menu_height = 360
        self.menu_rect = pygame.Rect(
            (self.display_surface.get_width() - menu_width) / 2,
            (self.display_surface.get_height() - menu_height) / 2,
            menu_width,
            menu_height)

        # menu text
        text = COMICORO[50].render('Menu', True, BLACK)
        text_rect = text.get_rect(
            center=(self.display_surface.get_width() / 2, 
                    self.display_surface.get_height() / 2 - 120))

        self.menu_text = text, text_rect

        # exit text
        text = COMICORO[50].render('Exit', True, BLACK)
        text_rect = text.get_rect(
            center=(self.display_surface.get_width() / 2, 
                    self.display_surface.get_height() / 2 + 120))

        self.exit_text = text, text_rect
        self.yellow_exit_text = color_image(self.exit_text[0], YELLOW)
    
    def menu_popup(self):
        global game_state

        if self.pause_button.active:
            game_state['unpaused'] = False
            pygame.draw.rect(
                self.display_surface,
                BROWN,
                self.menu_rect)

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.menu_rect, 
                5)

            self.display_surface.blit(*self.menu_text)
            if self.exit_text[1].collidepoint(pygame.mouse.get_pos()):
                self.display_surface.blit(self.yellow_exit_text, self.exit_text[1])
                if pygame.mouse.get_pressed()[0]:
                    game_state['runtime'] = False

            else:
                self.display_surface.blit(*self.exit_text)

        else:
            game_state['unpaused'] = True

    def draw(self):
        for sprite in self.sprites():
            self.display_surface.blit(sprite.image, sprite.rect.topleft)

        self.menu_popup()

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Button(pygame.sprite.Sprite):
    def __init__(self, coords, images:dict, groups, optional_key=False, work_paused=False):
        super().__init__(groups)
        self.width, self.height = 100, 100

        self.sprites = images
        for key, image in images.items():
            self.sprites[key] = pygame.transform.scale(image, (self.width, self.height))

        self.image = self.sprites['inactive']
        self.rect = self.image.get_rect(bottomright=coords)

        self.optional_key = optional_key
        self.work_paused = work_paused

        self.pressed = False
        self.active = False

    def press_button(self):
        global game_state

        left_click = pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos())
        button_disabled = not game_state['unpaused']

        if self.work_paused:
            button_disabled = False
            
        key_press = False
        if self.optional_key:
            key_press = pygame.key.get_pressed()[self.optional_key]
        
        # checks for left click or optional to popup menu
        if (left_click or key_press) and not self.pressed and not button_disabled:
            self.pressed = True
            self.active = not self.active

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
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.inventory_button = Button(
            (self.display_surface.get_width() - 100, self.display_surface.get_height()),
            {'inactive': IMAGES['backpack_closed'].copy(), 'active': IMAGES['backpack_opened'].copy()},
            self,
            optional_key=pygame.K_q)

        # inventory background
        inventory_width = 400
        inventory_height = 475
        self.inventory_rect = pygame.Rect(
            4,
            (self.display_surface.get_height() - inventory_height) - 4,
            inventory_width,
            inventory_height)

        self.inventory_surface = pygame.Surface((self.inventory_rect.width, self.inventory_rect.height))

        # inventory items
        self.item_box = IMAGES['item_box']
        self.item_box = pygame.transform.scale(self.item_box, (60, 60))

        # scroll
        self.scroll = 0
        self.scroll_acceleration = 0
        self.scroll_velocity = 0
        self.scroll_max_velocity = 7

    def add_item(self, name, image, tooltip, count):
        """Adds items to the inventory, stacking if it is already present"""
        inventory = [item for item in self.sprites() if item != self.inventory_button and item.name == name]

        # if the item already exists in inventory
        if inventory:
            inventory[0].count += count
        
        # adds a new item into the inventory
        else:
            Item(str(name), image, tooltip, count, self)

    def show_inventory(self):
        """Displays inventory"""
        self.display_surface.blit(
            self.inventory_surface,
            (self.inventory_rect.left, self.inventory_rect.top))

        self.inventory_surface.fill(BROWN)
        pygame.draw.rect(
            self.display_surface,
            DARK_BROWN,
            self.inventory_rect,
            5)

        # displays inventory items
        column = 0
        row = 0
        for item in self.sprites():
            if item != self.inventory_button:
                self.inventory_surface.blit(
                    self.item_box, 
                    (column * (self.item_box.get_width() + 15) + 20,
                    row * (self.item_box.get_height() + 15) + 20 - self.scroll)) # self.inventory_rect.top

                item.rect.x = column * (self.item_box.get_width() + 15) + 20
                item.rect.y = row * (self.item_box.get_height() + 15) + 20 - self.scroll # self.inventory_rect.top

                self.inventory_surface.blit(
                    item.image,
                    item.rect.topleft)

                item.show_tooltip()

                # displays item count when the player has multiple copies
                if item.count > 1:
                    text = COMICORO[25].render(str(item.count), True, WHITE)
                    text_rect = text.get_rect(
                        bottomright=(
                            item.rect.right - 5,
                            item.rect.bottom - 5))

                    self.inventory_surface.blit(text, text_rect)

                column += 1
                if not column % 5 and column != 0:
                    column = 0
                    row += 1

    def scroll_inventory(self):
        """Scrolls the inventory with the mouse wheel"""
        global event

        if self.inventory_rect.collidepoint(pygame.mouse.get_pos()):
            if len(self.sprites()) > 30:
                if event.type == pygame.MOUSEWHEEL:
                    if event.type:
                        self.scroll_acceleration = self.scroll_max_velocity * event.y / abs(event.y)

                        self.scroll_velocity += self.scroll_acceleration
                        self.scroll_velocity *= 0.5

                    else:
                        # movement decay when input is not received
                        self.scroll_velocity *= 0.7
                        self.scroll_acceleration = 0 

                    # movement decay when the speed is low
                    if abs(self.scroll_velocity) < 0.1:
                        self.scroll_velocity = 0

                    if abs(self.scroll_velocity) < 0.1:
                        self.scroll_velocity = 0

                    self.scroll += self.scroll_velocity
                    
                    max_scroll = (math.ceil((len(self.sprites()) - 1) / 5) - 6) * (self.item_box.get_height() + 15)
                    if self.scroll < 0:
                        self.scroll = 0  

                    elif self.scroll > max_scroll:
                        self.scroll = max_scroll

    def draw(self):
        if self.inventory_button.active:      
            self.show_inventory()
            self.scroll_inventory()
            
        self.display_surface.blit(self.inventory_button.image, self.inventory_button.rect.topleft)

    def update(self):
        """Handles events"""
        for sprite in self.sprites():
            sprite.update()


class Item(pygame.sprite.Sprite):
    def __init__(self, name, image, tooltip, count, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.width, self.height = 60, 60

        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()

        self.name = name
        self.count = count

        self.tooltip = ""
        self.tooltip_rect = pygame.Rect(self.rect.x, self.rect.y, 100, 100)
        
        text = COMICORO[20].render(self.name.title(), True, BLACK)
        text_rect = text.get_rect(
            center=self.rect.center)

        self.tooltip_text = [text, text_rect]

    def show_tooltip(self):
        """Displays tooltip when hovered over"""
        global player

        mouse_coords = list(pygame.mouse.get_pos()) # hard coded fixed margin of 5
        mouse_coords[0] -= 5
        mouse_coords[1] += player.inventory.inventory_rect.height - RESOLUTION[1] + 5

        if self.rect.collidepoint(mouse_coords):
            self.tooltip_rect.topleft = [i + 10 for i in pygame.mouse.get_pos()]

            self.tooltip_text[1] = [i + 10 for i in self.tooltip_rect.topleft]

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.tooltip_rect)

            pygame.draw.rect(
                self.display_surface,
                DARK_BROWN,
                self.tooltip_rect,
                5)

            self.display_surface.blit(*self.tooltip_text)
            

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 45, 45
        self.bar_width, self.bar_height = 120, 15

        self.image = IMAGES['heart'].copy()
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
        self.bar = pygame.Rect(
            self.rect.right,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

        self.total_bar = self.bar.copy()

        text = COMICORO[20].render(str(""), True, BLACK)
        text_rect = text.get_rect(midleft=self.bar.midleft)
        text_rect.left += self.total_bar.width * 0.25
        self.stat_text = [text, text_rect]

    def draw(self, target):
        pygame.draw.rect(self.display_surface, PECAN, self.total_bar, 2, 3)
        ratio = target.health['current'] / target.health['total']
        if ratio > 1:
            ratio = 1

        self.bar.width = self.bar_width * ratio
        if ratio > 0: # only display the bar when  the player has health
            pygame.draw.rect(self.display_surface, RED, self.bar, 0, 2)
            pygame.draw.rect(self.display_surface, BLOOD_RED, self.bar, 2, 3)

        self.stat_text[0] = COMICORO[20].render(str(target.health['current']), True, BLACK)
        self.display_surface.blit(*self.stat_text)


class SpeedBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 45, 45
        self.bar_width, self.bar_height = 120, 15

        self.image = IMAGES['lightning'].copy()
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
        self.bar = pygame.Rect(
            self.rect.right,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

        text = COMICORO[20].render(str(""), True, BLACK)
        text_rect = text.get_rect(midleft=self.bar.midleft)
        text_rect.left += self.bar.width * 0.25
        self.stat_text = [text, text_rect]

    def draw(self, target):
        pygame.draw.rect(self.display_surface, YELLOW, self.bar, 0, 3)
        pygame.draw.rect(self.display_surface, GOLD, self.bar, 2, 3)

        self.stat_text[0] = COMICORO[20].render(str(target.speed['current']), True, BLACK)
        self.display_surface.blit(*self.stat_text)


class AttackBar(pygame.sprite.Sprite):
    def __init__(self, coords, groups):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()

        self.width, self.height = 45, 45
        self.bar_width, self.bar_height = 120, 15

        self.image = IMAGES['sword'].copy()
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=coords)
        self.bar = pygame.Rect(
            self.rect.right,
            self.rect.centery - self.bar_height / 2,
            self.bar_width,
            self.bar_height)

        text = COMICORO[20].render(str(""), True, BLACK)
        text_rect = text.get_rect(midleft=self.bar.midleft)
        text_rect.left += self.bar.width * 0.25
        self.stat_text = [text, text_rect]

    def draw(self, target):
        pygame.draw.rect(self.display_surface, GREY, self.bar, 0, 3)
        pygame.draw.rect(self.display_surface, DARK_GREY, self.bar, 2, 3)

        self.stat_text[0] = COMICORO[20].render(str(target.attack['current']), True, BLACK)
        self.display_surface.blit(*self.stat_text)


class Bars(pygame.sprite.Group):
    def __init__(self, coords):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.coords = pygame.math.Vector2(coords)

        padding = 40
        self.padding_step = 30
        bars = (HealthBar, SpeedBar, AttackBar)
        for bar in bars:
            bar = bar(
                (self.coords[0], self.coords[1] + padding),
                self)

            padding += self.padding_step

        self.width = bar.bar.right + 10
        self.height = bar.rect.top - self.coords.y + 50

        self.rect = pygame.Rect(self.coords, (self.width, self.height))
        self.exp_rect = pygame.Rect(self.coords, (60, 30))

        name_text = COMICORO[25].render('', True, BLACK)
        name_text_rect = name_text.get_rect(
            center=(self.coords.x + self.width / 4,
                    self.coords.y + self.padding_step))

        self.name_text = [name_text, name_text_rect]

        exp_text = COMICORO[25].render('', True, BLACK)
        exp_text_rect = exp_text.get_rect(center=self.exp_rect.center)

        self.exp_text = [exp_text, exp_text_rect]
       
    def draw(self, targets):
        if len(targets) > 0:
            if len(targets) > 1:
                for target in targets:
                    if (target.in_combat or target.rect.collidepoint(Cursor.offset_mouse_pos())):
                        break

                    else:
                        target = False

            else:
                target = targets.sprites()[0]

            # draws the card of the target's health, speed, and attack
            if target and target.show_stats:
                pygame.draw.rect(self.display_surface, BROWN, self.rect, 0, 3)
                pygame.draw.rect(self.display_surface,DARK_BROWN, self.rect, 3, 3)

                self.name_text[0] = COMICORO[25].render(f'{target.name} lvl {target.level}', True, BLACK)
                self.display_surface.blit(*self.name_text)

                # blits the bar
                for sprite in self.sprites():
                    self.display_surface.blit(sprite.image, sprite.rect.topleft)
                    sprite.draw(target)

                # displays exp if the cursor is hovered over the name
                if self.name_text[1].collidepoint(pygame.mouse.get_pos()):
                    if target.exp_levels:
                        text = f'exp {target.exp} / {target.exp_levels[target.level - 1]}'

                    else:
                        text = f'exp {target.exp}'


                    self.exp_text[0] = COMICORO[25].render(text, True, BLACK)
                    self.exp_text[1] = self.exp_text[0].get_rect(center=self.exp_rect.center)

                    self.exp_rect.width = self.exp_text[1].width + 20
                    self.exp_rect.topleft = pygame.mouse.get_pos()

                    pygame.draw.rect(self.display_surface,
                                     BROWN, self.exp_rect)
                                     
                    pygame.draw.rect(self.display_surface,
                                     DARK_BROWN, self.exp_rect, 3)

                    self.display_surface.blit(*self.exp_text)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, tile_size, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        self.tile_size = tile_size

        self.image = IMAGES['cursor'].copy()
        self.image = pygame.transform.scale(self.image, (100, 100))

        self.rect = self.image.get_rect(center=(0, 0))

        self.sprite_layer = 4

    def update(self):
        global player

        coords = self.offset_mouse_pos()
        coords[0] = round(coords[0] / TILE_SIZE) * TILE_SIZE
        coords[0] -= player.rect.centerx - self.display_surface.get_width() / 2

        coords[1] = round(coords[1] / TILE_SIZE) * TILE_SIZE
        coords[1] -= player.rect.centery - \
            self.display_surface.get_height() / 2

        self.rect.center = coords

    @staticmethod
    def offset_mouse_pos():
        global player

        display_surface = pygame.display.get_surface()
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += player.rect.centerx - display_surface.get_width() / 2
        mouse_pos[1] += player.rect.centery - display_surface.get_height() / 2

        return mouse_pos


class GenericNPC:
    def movement(self):
        '''Handles movement'''
        global player, collision_group

        self.acceleration = pygame.math.Vector2(player.rect.centerx - self.rect.centerx,
                                                player.rect.centery - self.rect.centery)

        if (self.acceleration.length() < self.detection_distance 
            and not self.in_combat):
            if self.acceleration.length() > 0: 
                self.acceleration.scale_to_length(self.max_velocity) 

            self.velocity += self.acceleration
            self.velocity *= 0.5

        else:
            # movement decay
            self.velocity *= 0.8
            self.acceleration.x = 0
            self.acceleration.y = 0
        
        
        # movement decay when the speed is low
        if abs(self.velocity.x) < self.max_velocity / 100:
            self.velocity.x = 0

        if abs(self.velocity.y) < self.max_velocity / 100:
            self.velocity.y = 0

        self.coords += self.velocity
        self.rect.center = self.coords

    def collision(self):
            '''Handles collision'''
            global collision_group, level

            if abs(self.velocity.x) > 0 or abs(self.velocity.y) > 0:
                margin = pygame.math.Vector2(self.width / 8, self.height / 2.5)
                for sprite in collision_group:
                    collision_distance = pygame.math.Vector2((self.rect.width + sprite.rect.width) / 2,
                                                            (self.rect.height + sprite.rect.height) / 2)

                    distance = pygame.math.Vector2(self.rect.centerx - sprite.rect.centerx,
                                                self.rect.centery - sprite.rect.centery)

                    # checks if the distance of the sprites are within collision distance
                    if (abs(distance.x) + margin.x <= collision_distance.x
                        and abs(distance.y) + margin.y <= collision_distance.y):

                        # horizontal collision
                        if abs(distance.x) + margin.x > abs(distance.y) + margin.y:
                            # left collision
                            if distance.x > 0 and self.velocity.x < 0:
                                self.rect.left = sprite.rect.right - margin.x
                                
                            # right collision
                            elif distance.x < 0 and self.velocity.x > 0:
                                self.rect.right = sprite.rect.left + margin.x

                            self.coords[0] = self.rect.centerx
                            self.velocity.x = 0

                        # vertical collision
                        if abs(distance.y) + margin.y > abs(distance.x) + margin.x:
                            # bottom collision
                            if distance.y < 0 and self.velocity.y > 0:
                                self.rect.bottom = sprite.rect.top + margin.y
                                
                            # top collision
                            elif distance.y > 0 and self.velocity.y < 0:
                                self.rect.top = sprite.rect.bottom - margin.y

                            self.coords[1] = self.rect.centery
                            self.velocity.y = 0

                # left edge map
                if self.rect.left < level.rect.left + margin.x:
                    self.rect.left = level.rect.left + margin.x
                    self.coords[0] = self.rect.centerx
                    self.velocity.x = 0

                # right edge map
                elif self.rect.right > level.rect.right - margin.x:
                    self.rect.right = level.rect.right - margin.x
                    self.coords[0] = self.rect.centerx
                    self.velocity.x = 0

                # top edge map
                if self.rect.bottom < level.rect.top - margin.y:
                    self.rect.bottom = level.rect.top - margin.y
                    self.coords[1] = self.rect.centery
                    self.velocity.y = 0

                # bottom edge map
                elif self.rect.top > level.rect.bottom + margin.y:
                    self.rect.top = level.rect.bottom + margin.y
                    self.coords[1] = self.rect.centery
                    self.velocity.y = 0

    def face_enemy(self, target):
        if self.rect.centerx < target.rect.centerx:
            self.facing = 'right'

        else:
            self.facing = 'left'

    def attack_enemy(self, target_group):
        global camera_group
        # checks if the player mask overlaps an enemy mask
        if (pygame.sprite.spritecollide(self, target_group, False)
            and pygame.sprite.spritecollide(self, target_group, False, pygame.sprite.collide_mask)
            and self.health['current'] > 0):

            distance = pygame.math.Vector2(self.rect.center)
            closest_distance = lambda enemy: distance.distance_to(enemy.rect.center)
            enemies = target_group.sprites()
            enemy = sorted(enemies, key=closest_distance)[0] # closest enemy
            self.face_enemy(enemy)

            if not self.in_combat and enemy.health['current'] > 0:
                self.in_combat = True
                self.show_stats = True
                self.animation_time = pygame.time.get_ticks()
                self.cooldown = self.attack_cooldown
                self.frame = 0

            if self.in_combat:
                if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.cooldown:
                    self.attacking = True
                    self.frame = 0

                # only deal damage when animation ends
                if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                    if pygame.time.get_ticks() - self.animation_time > self.cooldown:
                        enemy.hurt(self.attack['current'], self.crit_chance['current'])
                        if enemy.health['current'] <= 0:
                            self.in_combat = False
                            self.exp += enemy.exp
        else:
            self.in_combat = False
            self.attacking = False
            self.cooldown = self.animation_cooldown

    def check_state(self):
        if not self.in_combat:
            self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        if self.health['current'] < 0:
            # sprite dies
            self.health['current'] = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = player.animation_cooldown

            for i in range(5):
                x_offset = round((self.rect.right - self.rect.left) / 4)
                x = random.randint(
                    self.rect.centerx - x_offset, 
                    self.rect.centerx + x_offset)

                y_offset = round((self.rect.bottom - self.rect.top) / 4)
                y = random.randint(
                    self.rect.centery - y_offset, 
                    self.rect.centery + y_offset)

                dust = Particle(
                    (x, y),
                    [randomize(self.rect.width / 2, 0.05) for i in range(2)],
                    f'dust{random.randint(1, 3)}',
                    camera_group)

                dust.velocity.y = -2

            self.kill()
            del self

    def hurt(self, attack, crit_chance):
        text_coords = (
            random.randint(
                round((self.rect.left + self.rect.centerx) / 2),
                round((self.rect.right + self.rect.centerx) / 2)),
            self.rect.top)

        dodge = self.dodge_chance['current'] >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2

                text = COMICORO[35].render(str(damage), True, BLOOD_RED)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                camera_group.texts.append(text)

            else:
                text = COMICORO[25].render(str(damage), True, RED)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                camera_group.texts.append(text)

            self.health['current'] -= damage

        else:
            text = COMICORO[20].render('Dodged', True, GOLD)
            text_rect = text.get_rect(center=text_coords)
            text = TextPopUp(text, text_rect)
            text.velocity.y = -5

            camera_group.texts.append(text)

    def animation(self):
        '''Handles animation'''

        # loops frames
        if self.frame >= len(self.animation_types[self.action]):
            self.frame = 0

        # set image
        self.image = self.animation_types[self.action][self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1

        # reflects over y-axis if facing left
        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)


class Player(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size
        
        self.in_combat = False
        self.attacking = False
        self.show_stats = True

        self.action = 'idle'
        self.facing = 'right'
        self.name = 'Player'

        # movement
        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_velocity = 4

        # stats
        self.exp = 0 # max exp is 9900
        self.exp_levels = [i for i in range(100, 10000, 100)]
        self.level = 1
        while self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

        self.bonuses = {'health': 0,
                        'speed': 0,
                        'attack': 0}

        self.health = {'current': 100,
                       'total': 100,
                       'base': 100}

        self.speed = {'current': 10,
                      'total': 10,
                      'base': 10}

        self.attack = {'current': 20,
                       'total': 20,
                       'base': 20}

        self.crit_chance = {'current': 0.05,
                            'base': 0.05}

        self.dodge_chance = {'current': 0.01,
                             'base': 0.01}

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'run': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'./sprites/player/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'knight_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.coords = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1200 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.speed['current']) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown
        self.set_stats()

        self.sprite_layer = 1

        self.inventory = Inventory()
        #self.inventory.add_item('wood sword', IMAGES['wood_sword'], 1)
        

        self.light_size = pygame.math.Vector2(700, 700)

        self.light = IMAGES['soft_circle'].copy()
        self.light = pygame.transform.scale(self.light, [int(dimension) for dimension in self.light_size])
        self.light = color_image(self.light, LIGHT_GREY, transparency=255)

    def set_stats(self):
        '''Scales stats according to its base and bonuses'''
        stats = {'health': self.health,
                 'speed': self.speed,
                 'attack': self.attack}

        for type in stats:
            ratio = stats[type]['current'] / stats[type]['total']

            stats[type]['total'] = round(stats[type]['base']
                                         * (1 + self.bonuses[type])
                                         * (1.05**(self.level - 1)))

            stats[type]['current'] = round(ratio * stats[type]['total'])

            self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
            if self.crit_chance['current'] > 0.5: # crit chance caps at 50%
                self.crit_chance['current'] = 0.5

            self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
            if self.dodge_chance['current'] > 0.33: # dodge chance caps at 33%
                self.dodge_chance['current'] = 0.33

            self.attack_cooldown = (1200 - self.speed['current']) / len(self.animation_types['attack'])
            if self.attack_cooldown < 200:
                self.attack_cooldown = 200

    def movement(self):
        '''Handles movement'''
        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            # creates movement using falsy and truthy values that evaluate to 0 and 1
            self.acceleration = pygame.math.Vector2(right - left, down - up)
            if self.acceleration.length_squared() > 0:  # checks if the player is moving
                # converts the coordinates to a vector according to the radius
                self.acceleration.scale_to_length(self.max_velocity)
                self.velocity += self.acceleration
                self.velocity *= 0.5

            else:
                # movement decay when input is not received
                self.velocity *= 0.8
                self.acceleration.x = 0
                self.acceleration.y = 0

            # movement decay when the speed is low
            if abs(self.velocity.x) < self.max_velocity / 100:
                self.velocity.x = 0

            if abs(self.velocity.y) < self.max_velocity / 100:
                self.velocity.y = 0

            self.coords += self.velocity
            self.rect.center = self.coords

    def leveling_up(self):
        '''Increases player level when they reach exp cap'''
        if self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

    def check_state(self):
        if not self.in_combat:
            if self.velocity.length_squared() > 0:
                self.action = 'run'

                if self.velocity.x < 0:
                    self.facing = 'left'

                elif self.velocity.x > 0:
                    self.facing = 'right'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

    def hurt(self, attack, crit_chance):
        text_coords = (
            random.randint(
                round((self.rect.left + self.rect.centerx) / 2),
                round((self.rect.right + self.rect.centerx) / 2)),
            self.rect.top)

        dodge = self.dodge_chance['current'] >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2

                text = COMICORO[35].render(str(damage), True, ORANGE)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                camera_group.texts.append(text)

            else:
                text = COMICORO[25].render(str(damage), True, TANGERINE)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                camera_group.texts.append(text)

            self.health['current'] -= damage

        else:
            text = COMICORO[20].render('Dodged', True, GOLD)
            text_rect = text.get_rect(center=text_coords)
            text = TextPopUp(text, text_rect)
            text.velocity.y = -5

            camera_group.texts.append(text)

        if self.health['current'] < 0:
            # sprite dies
            self.health['current'] = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = player.animation_cooldown

    def update(self):
        '''Handles events'''
        global enemy_group

        self.movement()
        self.collision()
        self.attack_enemy(enemy_group)
        self.check_state()
        self.animation()
        self.leveling_up()


class Ghost(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = True

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Ghost'

        # movement
        self.detection_distance = 350
        self.acceleration = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_velocity = 2

        # stats
        self.exp = 15
        self.exp_levels = False
        self.level = level

        self.health = {'current': round(30 * (1.1**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(10 * (1.1**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(6 * (1.1**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.crit_chance = {'current': 0.05,
                            'base': 0.05}

        self.dodge_chance = {'current': 0.1,
                             'base': 0.1}

        self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
        if self.crit_chance['current'] > 0.5:
            self.crit_chance['current'] = 0.5

        self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
        if self.dodge_chance['current'] > 0.33:
            self.dodge_chance['current'] = 0.33

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'run': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'./sprites/enemies/ghost/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'ghost_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.coords = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.speed['current']) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1
    
    def check_state(self):
        if not self.in_combat:
            if self.velocity.length_squared() > 0:
                self.action = 'run'

                if self.velocity.x < 0:
                    self.facing = 'left'

                elif self.velocity.x > 0:
                    self.facing = 'right'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        if self.health['current'] < 0:
            # sprite dies
            self.health['current'] = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = player.animation_cooldown

            for i in range(5):
                x_offset = round((self.rect.right - self.rect.left) / 4)
                x = random.randint(
                    self.rect.centerx - x_offset, 
                    self.rect.centerx + x_offset)

                y_offset = round((self.rect.bottom - self.rect.top) / 4)
                y = random.randint(
                    self.rect.centery - y_offset, 
                    self.rect.centery + y_offset)

                dust = Particle(
                    (x, y),
                    [randomize(self.rect.width / 2, 0.05) for i in range(2)],
                    f'dust{random.randint(1, 3)}',
                    camera_group)

                dust.velocity.y = -2

            self.kill()
            del self

    def update(self):
        '''Handles events'''
        global player_group

        self.movement()
        self.collision()
        self.attack_enemy(player_group)
        self.check_state()
        self.animation()


class Mimic(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Mimic'

        # stats
        self.exp = 50
        self.exp_levels = False
        self.level = level

        self.health = {'current': round(100 * (1.2**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(20 * (1.15**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(7 * (1.05**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.crit_chance = {'current': 0.15,
                            'base': 0.15}

        self.dodge_chance = {'current': 0,
                             'base': 0}

        self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
        if self.crit_chance['current'] > 0.5:
            self.crit_chance['current'] = 0.5

        self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
        if self.dodge_chance['current'] > 0.33:
            self.dodge_chance['current'] = 0.33

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'./sprites/enemies/mimic/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'mimic_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.coords = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.speed['current']) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1

    def update(self):
        '''Handles events'''
        global player_group

        self.attack_enemy(player_group)
        self.check_state()
        self.animation()


class Sunflower(pygame.sprite.Sprite, GenericNPC):
    def __init__(self, coords: list, size: list, level, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Sunflower'

        # stats
        self.exp = 5
        self.exp_levels = False
        self.level = level

        self.health = {'current': round(25 * (1.05**(self.level - 1)))}
        self.health['total'] = self.health['current']

        self.attack = {'current': round(7 * (1.05**(self.level - 1)))}
        self.attack['total'] = self.attack['current']

        self.speed = {'current': round(5 * (1.025**(self.level - 1)))}
        self.speed['total'] = self.speed['current']

        self.crit_chance = {'current': 0.05,
                            'base': 0.05}

        self.dodge_chance = {'current': 0,
                             'base': 0}

        self.crit_chance['current'] = round(self.crit_chance['base'] + self.speed['current'] / 500, 2)
        if self.crit_chance['current'] > 0.5:
            self.crit_chance['current'] = 0.5

        self.dodge_chance['current'] = round(self.dodge_chance['base'] + self.speed['current'] / 750, 2)
        if self.dodge_chance['current'] > 0.33:
            self.dodge_chance['current'] = 0.33

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'./sprites/enemies/sunflower/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'sunflower_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, (self.width, self.height))

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.rect = self.image.get_rect(center=coords)
        self.coords = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.speed['current']) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

        self.sprite_layer = 1

    def update(self):
        '''Handles events'''
        global player_group

        self.attack_enemy(player_group)
        self.check_state()
        self.animation()


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.chest_sprites = {}
        self.chest_sprites['closed'] = IMAGES['chest_closed'].copy()
        self.chest_sprites['closed'] = pygame.transform.scale(
            self.chest_sprites['closed'], (self.width, self.height))

        self.chest_sprites['opened'] = IMAGES['chest_opened'].copy()
        self.chest_sprites['opened'] = pygame.transform.scale(
            self.chest_sprites['opened'], (self.width, self.height))
        self.image = self.chest_sprites['closed']

        self.rect = self.image.get_rect(center=coords)
        self.opened = False

        self.sprite_layer = 1

    def collision(self):
        global player

        # checks if the distance of the sprites are within collision distance
        if pygame.Rect.colliderect(self.rect, player.rect) and not self.opened:
            self.image = self.chest_sprites['opened']
            self.opened = True

            #player.inventory.add_item('Baguette', IMAGES['baguette'], random.randint(1, 3))
            #player.inventory.add_item('Oak Log', IMAGES['oak_log'], random.randint(1, 3))

    def update(self):
        self.collision()


class LevelExit(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = IMAGES['dirt_hole'].copy()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.sprite_layer = 1

    def update(self):
        global player_group, level

        if pygame.sprite.spritecollide(self, player_group, False):
            # checks if the player mask overlaps an enemy mask
            if pygame.sprite.spritecollide(self, player_group, False, pygame.sprite.collide_mask):
                level.floor_level += 1


class StaticTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, image: str, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = IMAGES[image].copy()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=coords)

        self.sprite_layer = 1


class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, images, groups):
        super().__init__(groups)
        self.width, self.height = size
        self.frame = 0

        self.animation_types = []
        num_of_frames = len(
            os.listdir(f'./sprites/decoration/animated/{images}'))

        for i in range(num_of_frames):
            image = IMAGES[f'{images}{i + 1}'].copy()
            image = pygame.transform.scale(image, size)

            self.animation_types.append(image)

        self.image = self.animation_types[self.frame]
        self.rect = self.image.get_rect(center=coords)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1200 / len(self.animation_types)

        self.sprite_layer = 1

    def animation(self):
        '''Handles animation'''
        # loops frames
        if self.frame >= len(self.animation_types):
            self.frame = 0

        # set image
        self.image = self.animation_types[self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.animation_cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1


class Torch(AnimatedTile):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(coords, size, 'torch', groups)
        self.sprite_layer = 2
        self.rect.centerx += random.randint(-1, 1) * 25
        self.rect.centery += 25

        self.smoke_time = pygame.time.get_ticks() + random.randint(1000, 2000)
        self.smoke_cooldown = randomize(4000, 0.2)
        
        self.smoke_frames = len(
            os.listdir(f'./sprites/particles/smoke'))

        self.light_size = pygame.math.Vector2(500, 500)

        self.light = IMAGES['soft_circle'].copy()
        self.light = pygame.transform.scale(self.light, [int(dimension) for dimension in self.light_size])
        self.light = color_image(self.light, MELLOW_YELLOW, transparency=100)

    def draw_smoke(self):
        if pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            self.smoke_time = pygame.time.get_ticks()
            self.smoke_cooldown = randomize(4000, 0.2)

            smoke = Particle(
                self.rect.center,
                [randomize(25, 0.1) for i in range(2)],
                f'smoke{random.randint(1, self.smoke_frames)}',
                camera_group)

            smoke.velocity.y = -4
            smoke.expiration_time = 500
            
    def update(self):
        self.animation()
        self.draw_smoke()


def randomize(value: int, offset: float):
    '''Randomizes the value with a +- deviation of the offset'''
    return random.randint(
        round(value * (1 - offset)),
        round(value * (1 + offset)))


def color_image(image, color, transparency=255):
    '''Recolors a surface'''
    image = image.copy()
    # zeros out rgb and preserves original transparency
    image.fill((0, 0, 0, 255), None, special_flags=pygame.BLEND_RGBA_MULT)

    # adds in new rgb values
    image.fill(color + (0,), None, pygame.BLEND_RGBA_ADD)

    if transparency:
        image.set_alpha(transparency)

    return image

# sets up pygame
pygame.init()
pygame.font.init()
pygame.display.set_caption('Novorus')

# sets the size of the screen; defaults to full screen
RESOLUTION = (1920, 1080)  
screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF | pygame.FULLSCREEN, 16)
clock = pygame.time.Clock()

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEMOTION])
from constants import *

# sprite groups
camera_group = CameraGroup()
collision_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()
cursor_group = pygame.sprite.GroupSingle()
light_group = LightSources(RESOLUTION)

menu = Menu()

player_bars = Bars((2, 2))
enemy_bars = Bars((2, player_bars.height + 4))

# hud
cursor = Cursor(TILE_SIZE, cursor_group)

# player
player = Player((0, 0), (75, 75), (camera_group, player_group, light_group))

# levels and map
level = Level(STARTING_FLOOR, TILE_SIZE)

while game_state['runtime']:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            game_state['runtime'] = False

    screen.fill((105, 162, 97))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitboxes=False)
    cursor_group.draw(screen)
    light_group.render_lighting(player)

    player_bars.draw(player_group)
    enemy_bars.draw(enemy_group)

    menu.draw()
    player.inventory.draw()
    level.draw()

    # updates
    if game_state['unpaused'] and not level.transitioning:
        camera_group.update()

    cursor_group.update()
    menu.update()
    player.inventory.update()
    level.update()

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()

#
