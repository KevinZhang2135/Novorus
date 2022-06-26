from turtle import right
import pygame
import os
import math
import random

# "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0


class Sprite(pygame.sprite.Sprite):
    def __init__(self, size: list, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        self.width, self.height = size

    def load_image(self, image):
        '''Loads an image according to the input'''
        image = pygame.image.load(os.path.join('sprites', image)).convert_alpha()
        image = pygame.transform.scale(image, (self.width, self.height))

        return image

    def load_text(self, text, coords, text_size, color):
        font = pygame.font.Font('comicoro.ttf', round(text_size))
        text = font.render(text, True, color)
        text_rect = text.get_rect(center = coords)
        
        return text, text_rect


class Player(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        self.image = self.load_image('knight_walk1.png')
        self.rect = self.image.get_rect(center=coords)
        self.rect.inflate_ip(self.width * -0.3, 0)

        self.colliding = False
        self.in_combat = False
        self.attacking = False

        self.move_speed = 5
        self.ticks = 0

        self.facing = 'right'
        self.name = 'Player'

        self.health = {'current': 10,
                       'total': 100}

        self.attack = {'current': 20,
                       'total': 20}

        self.speed = {'current': 50,
                      'total': 50}

    def movement(self):
        '''Handles movement'''
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        up = keys[pygame.K_UP] or keys[pygame.K_w]

        # creates movement using falsy and truthy values that evaluate to 0 and 1
        move = pygame.math.Vector2(right - left, down - up)
        if move.length_squared() > 0:  # checks if the player is moving
            # converts the coordinates to a vector according to the radius
            move.scale_to_length(self.move_speed)

        if not self.in_combat:
            self.rect.centerx += move.x
            self.rect.centery += move.y

    def collision(self, sprites):
        '''Handles collision'''
        for sprite in sprites:
            collision_distance = pygame.math.Vector2((self.rect.width + sprite.rect.width) / 2,
                                                     (self.rect.height + sprite.rect.height) / 2)

            distance = pygame.math.Vector2(self.rect.centerx - sprite.rect.centerx,
                                           self.rect.centery - sprite.rect.centery)

            # checks if the distance of the sprites are within collision distance
            if abs(distance.x) <= collision_distance.x and abs(distance.y) <= collision_distance.y:
                # horizontal collision
                if abs(distance.x) > abs(distance.y):
                    # left collision
                    if distance.x > 0:
                        self.rect.left = sprite.rect.right

                    # right collision
                    if distance.x < 0:
                        self.rect.right = sprite.rect.left

                # vertical collision
                else:
                    # bottom collision
                    if distance.y < 0:
                        self.rect.bottom = sprite.rect.top

                    # top collision
                    if distance.y > 0:
                        self.rect.top = sprite.rect.bottom

    def animation(self):
        '''Handles animation'''
        movement_sprites = ['knight_walk1.png',
                            'knight_walk2.png',
                            'knight_walk1.png',
                            'knight_walk3.png']

        idle_sprites = ['knight_walk1.png',
                        'knight_idle1.png',
                        'knight_walk1.png',
                        'knight_idle2.png']

        combat_sprites = ['knight_walk1.png',
                          'knight_attack1.png',
                          'knight_attack2.png',
                          'knight_attack3.png']

        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            if left or right or down or up:
                self.image = self.load_image(movement_sprites[math.floor(self.ticks / 30)])

                if left:
                    self.facing = 'left'

                elif right:
                    self.facing = 'right'

            else:
                self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])

        else:
            if self.attacking:
                self.image = self.load_image(combat_sprites[math.floor(self.ticks / 30)])

            else:
                self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, collision_group):
        '''Handles events'''
        self.movement()
        self.collision(collision_group)
        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
            

class Ghost(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        self.image = self.load_image('ghost_idle1.png')
        self.rect = self.image.get_rect(center=coords)
        self.rect.inflate_ip(self.width * -0.3, self.height * -0.15)

        self.in_combat = False
        self.attacking = False

        self.move_speed = 2
        self.ticks = random.randint(0, 30)

        self.facing = random.choice(['left', 'right'])
        self.name = 'Ghost'

        self.health = {'current': 30,
                       'total': 30}

        self.attack = {'current': 10,
                       'total': 10}

        self.speed = {'current': 30,
                      'total': 30}

    def animation(self):
        '''Handles animation'''
        idle_sprites = ['ghost_idle1.png',
                        'ghost_idle2.png',
                        'ghost_idle3.png',
                        'ghost_idle2.png']

        combat_sprites = ['ghost_idle1.png',
                          'ghost_attack1.png',
                          'ghost_attack2.png',
                          'ghost_attack3.png']

        if not self.in_combat:
           self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])

        else:
            if self.attacking:
                self.image = self.load_image(combat_sprites[math.floor(self.ticks / 30)])

            else:
                self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, collision_group):
        '''Handles events'''
        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
        

class Wall(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        self.image = self.load_image('gray_bricks.png')
        self.rect = self.image.get_rect(center=coords)


class Ambience(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, ):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_size()[0] / 2
        self.half_height = self.display_surface.get_size()[1] / 2

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def custom_draw(self, player):
        '''Draws the screen according to player movement'''
        self.center_target(player)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.bottom):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


class Menu(Sprite):
    def __init__(self, groups):
        sprite_width = pygame.display.get_surface().get_height() * 3 / 32
        super().__init__((sprite_width, sprite_width), groups)

        menu_width = self.display_surface.get_height() / 3
        menu_height = self.display_surface.get_height() / 3

        self.image = self.load_image('menu1.png')
        self.rect = self.image.get_rect(
            bottomright=[self.display_surface.get_width(),
                    self.display_surface.get_height()])

        self.menu_rect = pygame.Rect(
            ((self.display_surface.get_width() - menu_width) / 2,
             (self.display_surface.get_height() - menu_height) / 2),
            (menu_width, menu_height))

        # menu text
        self.menu_text, self.menu_text_rect = self.load_text(
            'Menu', 
            (self.menu_rect.centerx, self.menu_rect.top + self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            (50, 50, 50))

        # exit text
        self.draw_exit_text((50, 50, 50))

        self.pressed = False
    
    def draw_exit_text(self, color):
        self.exit_text, self.exit_text_rect = self.load_text(
            'Exit', 
            (self.menu_rect.centerx, self.menu_rect.bottom - self.menu_rect.height / 8),
            self.menu_rect.width / 8,
            color)

    def draw(self):
        global paused

        if paused:
            pygame.draw.rect(self.display_surface,
                             (131, 106, 83), self.menu_rect, 0)

            pygame.draw.rect(self.display_surface,
                             (104, 84, 66), self.menu_rect, 5)

            self.display_surface.blit(self.menu_text, self.menu_text_rect)
            self.display_surface.blit(self.exit_text, self.exit_text_rect)

    def update(self):
        global paused
        global runtime

        pause_left_click = (pygame.mouse.get_pressed()[0]
                            and self.rect.collidepoint(pygame.mouse.get_pos()))

        escape_key = pygame.key.get_pressed()[pygame.K_ESCAPE]

        # checks for left click and escape_key to popup menu
        if (pause_left_click or escape_key) and not self.pressed:
            self.pressed = True
            paused = not paused

        elif not (pause_left_click or escape_key) and self.pressed:
            self.pressed = False

        if paused:
            self.image = self.load_image('menu2.png')

            if self.exit_text_rect.collidepoint(pygame.mouse.get_pos()):
                self.draw_exit_text((255, 231, 45))

                if pygame.mouse.get_pressed()[0]:
                    runtime = False

            else:
                self.draw_exit_text((50, 50, 50))

        else:
            self.image = self.load_image('menu1.png')


class Bar(Sprite):
    def __init__(self, coords, groups):
        sprite_width = pygame.display.get_surface().get_height() / 8
        super().__init__((sprite_width, sprite_width), groups)

        self.bar_height = self.display_surface.get_height() / 32
        self.coords = coords

    def draw(self, text):
        pygame.draw.rect(self.display_surface, self.light_color, self.bar, 0)
        pygame.draw.rect(self.display_surface, self.dark_color, self.bar, 3)

        self.text_surface, self.text_rect = self.load_text(
            text,
            self.bar.center,
            self.bar.height,
            (50, 50, 50))

        self.display_surface.blit(self.text_surface, self.text_rect)

    def set_health(self):
        self.image = self.load_image('heart.png')
        self.rect = self.image.get_rect(
            center=self.coords)

        self.bar = pygame.Rect(
            (self.rect.centerx, self.rect.centery - self.bar_height / 2),
            (self.rect.width * 1.5, self.bar_height))

        self.light_color = (211, 47, 47)
        self.dark_color = (198, 40, 40)

    def set_speed(self):
        self.image = self.load_image('lightning.png')
        self.rect = self.image.get_rect(
            center=coords)

        self.bar = pygame.Rect(
            (self.rect.centerx, self.rect.centery - self.bar_height / 2),
            (self.rect.width * 1.5, self.bar_height))

        self.light_color = (255, 231, 45)
        self.dark_color = (255, 219, 14)

    def set_attack(self):
        self.image = self.load_image('sword.png')
        self.rect = self.image.get_rect(
            center=coords)

        self.bar = pygame.Rect(
            (self.rect.centerx, self.rect.centery - self.bar_height / 2),
            (self.rect.width * 1.5, self.bar_height))

        self.light_color = (188, 188, 188)
        self.dark_color = (168, 168, 168)


pygame.init()
pygame.font.init()
pygame.display.set_caption('Novorus')

# sets the size of the screen; defaults to full screen
screen = pygame.display.set_mode()
clock = pygame.time.Clock()

camera_group = CameraGroup()
enemies = pygame.sprite.Group()
collision_group = pygame.sprite.Group()
hud_group = CameraGroup()

used_coords = []
coords = None

# ambience
size = [60, 40, 150]
objects = ['rock', 'grass', 'tree']
for j in range(100):
    obj = random.choice(objects)
    while coords in used_coords or not coords:
        coords = [round(random.randint(0, 2000), -2) for i in range(2)]

    used_coords.append(coords)
    decor = Ambience(
        coords, (size[objects.index(obj)], size[objects.index(obj)]), camera_group)

    variation = random.randint(1, 3)
    decor.image = decor.load_image(f'{obj}{variation}.png')
    decor.rect = decor.image.get_rect(center=coords)
    if random.randint(0, 1):
        decor.image = pygame.transform.flip(decor.image, True, False)

# enemies
size = [75, 75]
for i in range(10):
    while coords in used_coords or not coords:
        coords = [round(random.randint(0, 2000), -2) for i in range(2)]

    used_coords.append(coords)
    ghost = Ghost(coords, size, (camera_group, enemies))

# player
size = [75, 75]
coords = [1000, 1000]
player = Player(coords, size, camera_group)

# hud
menu = Menu(hud_group)

player_health_bar = Bar(coords, hud_group)
player_health_bar.set_health()

player_speed_bar = Bar(coords, hud_group)
player_speed_bar.set_speed()

player_attack_bar = Bar(coords, hud_group)
player_attack_bar.set_attack()


enemy_bars = []

ticks = 0
paused = True
runtime = True

while runtime:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            runtime = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # updates
    for enemy in enemies:
        if pygame.Rect.colliderect(player.rect, enemy.rect):
            # checks health before entering combat
            if player.health['current'] > 0 or enemy.health['current'] > 0:
                # sync ticks so combat immediately starts
                if not player.in_combat:
                    player.in_combat = True
                    enemy.in_combat = True

                    player.ticks = 0
                    enemy.ticks = 0
                
                # player and enemy face each other
                if player.rect.centerx < enemy.rect.centerx:
                    player.facing = 'right'
                    enemy.facing = 'left'

                else:
                    player.facing = 'left'
                    enemy.facing = 'right'

                # player animation for attacking
                if player.ticks == 0:
                    chance = random.randint(0, player.speed['current'] + enemy.speed['current'])
                    if chance < player.speed['current']:
                        # player attacks
                        player.attacking = True

                    else:
                        # enemy attacks
                        enemy.attacking = True

                # only deal damage after end of animation
                if player.ticks == 119 and player.attacking:
                    enemy.health['current'] -= player.attack['current']
                    player.attacking = False

                elif enemy.ticks == 119 and enemy.attacking:
                    player.health['current'] -= enemy.attack['current']
                    enemy.attacking = False

            # end of combat
            if player.health['current'] <= 0 or enemy.health['current'] <= 0:
                player.in_combat = False
                player.attacking = False

                enemy.in_combat = False
                enemy.attacking = False

                if enemy.health['current'] <= 0:
                    enemy.kill()
                    del enemy

                else:
                    pass

    if not paused:
        camera_group.update(collision_group)

    hud_group.update()

    # redraws sprites and images
    camera_group.custom_draw(player)

    # hud
    menu.draw()
    player_health_bar.draw(f"{player.health['current']} / {player.health['total']}")
    player_speed_bar.draw(f"{player.speed['current']}")
    player_attack_bar.draw(f"{player.attack['current']}")

    hud_group.draw(screen)

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()


#
