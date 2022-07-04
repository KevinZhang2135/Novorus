import pygame
import random

from libraries.background import *
from libraries.camera import *
from libraries.enemies import *
from libraries.interactables import *
from libraries.player import *
from libraries.tools import *
from libraries.ui import *

# "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0

ticks = 0
game_state = {'paused': True,
              'runtime': True,
              'fullscreen': True}

pygame.init()
pygame.font.init()
pygame.display.set_caption('Novorus')

# sets the size of the screen; defaults to full screen
screen = pygame.display.set_mode((1920, 1020), pygame.RESIZABLE)
clock = pygame.time.Clock()

camera_group = CameraGroup()
enemies = pygame.sprite.Group()
collision_group = pygame.sprite.Group()
hud_group = CameraGroup()

# hud
menu = Menu(hud_group)
player_bars = TargetBars((0, 0), hud_group)
enemy_bars = TargetBars((0, screen.get_height() * 11 / 64), hud_group)

# player
player = Player((0, 0), (75, 75), camera_group)

used_coords = [(0, 0)]
coords = None

wall = Ambience((100, 100), (100, 100), 'wall1.png',
                (camera_group, collision_group))

# ambience
size = (60, 40, 125, 100)
objects = ['rock', 'grass', 'tree']
for j in range(150):
    obj = random.choice(objects)
    while coords in used_coords or not coords:
        coords = [round(random.randint(-1500, 1500), -2) for i in range(2)]

    used_coords.append(coords)
    groups = [camera_group]
    variation = random.randint(1, 3)

    decor = Ambience(
        coords,
        [size[objects.index(obj)]] * 2,
        f'{obj}{variation}.png',
        groups)

# enemies
for i in range(20):
    while coords in used_coords or not coords:
        coords = [round(random.randint(-1500, 1500), -2) for i in range(2)]

    used_coords.append(coords)
    ghost = Ghost(coords, (60, 60), (camera_group, enemies))

# chests
for i in range(5):
    while coords in used_coords or not coords:
        coords = [round(random.randint(-1500, 1500), -2) for i in range(2)]

    used_coords.append(coords)
    chest = Chest(coords, (60, 60), (camera_group, collision_group))

while game_state['runtime']:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            game_state['runtime'] = False

    screen.fill((130, 200, 90))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitbox=True)

    # updates

    # checks if the player rect is within an enemy rect
    if pygame.sprite.spritecollide(player, enemies, False):
        # checks if the player mask overlaps an enemy mask
        if pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask):
            for enemy in enemies:
                # determines which enemy is withing the player rect
                if pygame.Rect.colliderect(player.rect, enemy.rect):
                    combat(player, enemy)
                    if player.in_combat:
                        enemy_bars.add_sprites(hud_group)
                        enemy_bars.draw(enemy)

                    break

    if not player.in_combat:
        enemy_bars.hide_sprites()

    if not game_state['paused']:
        camera_group.update(player, collision_group)

    hud_group.update(game_state)

    # hud
    player_bars.draw(player)
    hud_group.draw(screen)

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()


#
