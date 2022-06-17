import pygame
import os
import math
import random


class Sprite(pygame.sprite.Sprite):
    def __init__(self, size: list, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        
        self.width, self.height = size
        

    def load_image(self, image):
        '''Loads an image according to the input'''
        image = pygame.image.load(os.path.join(
            'sprites', image)).convert_alpha()
        image = pygame.transform.scale(image, (self.width, self.height))

        return image
        
    def load_text(self, coords, size, text, color):
        font = pygame.font.SysFont(None, round(size))
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=coords)
        
        self.display_surface.blit(text_surface, text_rect)
        

class Player(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        self.image = self.load_image('knight_walk1.png')
        self.rect = self.image.get_rect(center=coords)
        self.rect.inflate_ip(self.width * -0.3, 0)

        self.colliding = False
        self.move_speed = 3

        self.facing = 'right'
        self.ticks = 0
        
        self.health = {'current': 100,
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

        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        up = keys[pygame.K_UP] or keys[pygame.K_w]

        if left or right or down or up:
            self.image = self.load_image(
                movement_sprites[math.floor(self.ticks / 30)])

            if left:
                self.facing = 'left'

            elif right:
                self.facing = 'right'

        else:
            self.image = self.load_image(
                idle_sprites[math.floor(self.ticks / 30)])

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def battle(self, enemies):
        for enemy in enemies:
            if pygame.Rect.colliderect(self.rect, enemy.rect):
                self.health['current'] -= 9
                enemy.kill()
                del enemy

    def update(self, enemies, collision_group):
        '''Handles events'''
        self.movement()
        self.battle(enemies)
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

        self.move_speed = 2
        self.detection_distance = 350 * random.randint(3, 5) / 5
        self.ticks = random.randint(0, 30)

    def animation(self):
        '''Handles animation'''
        idle_sprites = ['ghost_idle1.png',
                        'ghost_idle2.png',
                        'ghost_idle3.png',
                        'ghost_idle2.png']

        self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])

    def update(self, *groups):
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
        
        ui_width = self.display_surface.get_width()
        ui_height = self.display_surface.get_height() / 8

        menu_width = self.display_surface.get_height() / 3
        menu_height = self.display_surface.get_height() / 3

        self.image = self.load_image('menu1.png')
        self.rect = self.image.get_rect(
            center=[self.display_surface.get_width() - ui_height / 2,
                    self.display_surface.get_height() - ui_height / 2])

        self.bg_rect = pygame.Rect(
            (0, ui_height * 7),
            (ui_width, ui_height))

        self.menu_rect = pygame.Rect(
            ((self.display_surface.get_width() - menu_width) / 2,
             (self.display_surface.get_height() - menu_height) / 2),
            (menu_width, menu_height))

        self.pressed = False

    def draw(self):
        global paused
        brown = (104, 84, 66)
        light_brown = (131, 106, 83)
        black = (50, 50, 50)
        
        pygame.draw.rect(self.display_surface, light_brown, self.bg_rect, 0)
        pygame.draw.rect(self.display_surface, brown, self.bg_rect, 5)

        if paused:
            pygame.draw.rect(self.display_surface,
                             light_brown, self.menu_rect, 0)
                             
            pygame.draw.rect(self.display_surface, brown, self.menu_rect, 5)
            self.load_text(
                (
                    self.menu_rect.centerx, 
                    self.menu_rect.top + self.menu_rect.height / 8),
                round(self.menu_rect.width / 8),
                'Menu',
                black)

    def update(self):
        global paused
        left_click = (pygame.mouse.get_pressed()[0]
                      and self.rect.collidepoint(pygame.mouse.get_pos()))

        escape_key = pygame.key.get_pressed()[pygame.K_ESCAPE]

        # checks for left click and escape_key to popup menu
        if (left_click or escape_key) and not self.pressed:
            self.pressed = True
            paused = not paused

        elif not (left_click or escape_key) and self.pressed:
            self.pressed = False

        if paused:
            self.image = self.load_image('menu2.png')

        else:
            self.image = self.load_image('menu1.png')


class HealthBar(Sprite):
    def __init__(self, groups):
        sprite_width = pygame.display.get_surface().get_height() / 8
        super().__init__((sprite_width, sprite_width), groups)
        
        bar_height = self.display_surface.get_height() / 32

        self.image = self.load_image('heart.png')
        self.rect = self.image.get_rect(
            center=[sprite_width / 2,
                    self.display_surface.get_height() - sprite_width / 2])

        self.bar = pygame.Rect(
            (self.rect.centerx, self.rect.centery - bar_height / 2),
            (self.rect.width * 1.5, bar_height))

    def draw(self, player):
        red = (211, 47, 47)
        blood_red = (198, 40, 40)
        black = (50, 50, 50)
        pygame.draw.rect(self.display_surface, red, self.bar, 0)
        pygame.draw.rect(self.display_surface, blood_red, self.bar, 2)
        
        self.load_text(
            self.bar.center,
            self.bar.height,
            '%s / %s' % (player.health['current'], player.health['total']),
            black)

class SpeedBar(Sprite):
    def __init__(self, groups):
        sprite_width = pygame.display.get_surface().get_height() / 8
        super().__init__((sprite_width, sprite_width), groups)
        
        bar_height = self.display_surface.get_height() / 32

        self.image = self.load_image('lightning.png')
        self.rect = self.image.get_rect(
            center=[sprite_width * 5 / 2,
                    self.display_surface.get_height() - sprite_width / 2])

        self.bar = pygame.Rect(
            (self.rect.centerx, self.rect.centery - bar_height / 2),
            (self.rect.width, bar_height))

    def draw(self, player):
        yellow = (255, 231, 45)
        gold = (255, 219, 14)
        black = (50, 50, 50)
        pygame.draw.rect(self.display_surface, yellow, self.bar, 0)
        pygame.draw.rect(self.display_surface, gold, self.bar, 2)
        
        self.load_text(
            self.bar.center,
            self.bar.height,
            str(player.speed['current']),
            black)
            
            
class AttackBar(Sprite):
    def __init__(self, groups):
        sprite_width = pygame.display.get_surface().get_height() / 8
        super().__init__((sprite_width, sprite_width), groups)
        
        bar_height = self.display_surface.get_height() / 32

        self.image = self.load_image('sword.png')
        self.rect = self.image.get_rect(
            center=[sprite_width * 8 / 2,
                    self.display_surface.get_height() - sprite_width / 2])

        self.bar = pygame.Rect(
            (self.rect.centerx, self.rect.centery - bar_height / 2),
            (self.rect.width, bar_height))

    def draw(self, player):
        grey = [189] * 3
        dark_grey = [158] * 3
        black = (50, 50, 50)
        pygame.draw.rect(self.display_surface, grey, self.bar, 0)
        pygame.draw.rect(self.display_surface, dark_grey, self.bar, 2)
        
        self.load_text(
            self.bar.center,
            self.bar.height,
            str(player.attack['current']),
            black)

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
    ghost = Ghost(coords, size, (camera_group, enemies, collision_group))

# player
size = [75, 75]
coords = [1000, 1000]
player = Player(coords, size, camera_group)
    
# hud
menu = Menu(hud_group)
health_bar = HealthBar(hud_group)
speed_bar = SpeedBar(hud_group)
attack_bar = AttackBar(hud_group)

ticks = 0
paused = True
runtime = True
while runtime:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            runtime = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                runtime = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # updates
    # camera_group.draw(screen)
    if not paused:
        camera_group.update(enemies, collision_group)

    hud_group.update()

    # redraws sprites and images
    camera_group.custom_draw(player)

    # hud
    menu.draw()
    health_bar.draw(player)
    speed_bar.draw(player)
    attack_bar.draw(player)
    
    hud_group.draw(screen)

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()





#