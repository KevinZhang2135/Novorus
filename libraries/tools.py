import pygame
import random
import os


def load_image(image, size: list):
    '''Loads an image according to the input'''
    image = pygame.image.load(os.path.join(
        'sprites', image)).convert_alpha()
    image = pygame.transform.scale(image, [round(i) for i in size])

    return image


def load_text(text, coords, text_size, color):
    font = pygame.font.Font('comicoro.ttf', round(text_size))
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=coords)

    return text, text_rect


def combat(player, enemy):
    # checks health before entering combat
    if player.health['current'] > 0 or enemy.health['current'] > 0:
        # sync ticks so combat immediately starts
        if not player.in_combat:
            player.in_combat = True
            enemy.in_combat = True

            player.ticks = 0

        # player and enemy face each other
        if player.rect.centerx < enemy.rect.centerx:
            player.facing = 'right'
            enemy.facing = 'left'

        else:
            player.facing = 'left'
            enemy.facing = 'right'

        # player animation for attacking
        if player.ticks == 0:
            chance = random.randint(
                0, player.speed['current'] + enemy.speed['current'])
            if chance < player.speed['current']:
                # player attacks
                player.attacking = True
                player.ticks =  20

            else:
                # enemy attacks
                enemy.attacking = True
                enemy.ticks = 40

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
