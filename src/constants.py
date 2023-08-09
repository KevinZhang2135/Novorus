from color import Color

import pygame 
import os
import math
import random

pygame.init()
pygame.display.set_mode()

# tile pixel size
TILE_SIZE = 100
HALF_TILE_SIZE = TILE_SIZE / 2
STARTING_FLOOR = 1

# file paths
LEVEL_PATH = '../levels'
SPRITE_PATH = '../sprites'
ITEM_PATH = '../items'

# retrieving image files for tooltips
IMAGES = {}
for (path, dirs, files) in os.walk(SPRITE_PATH, topdown=True):
    for file in files:
        file_name, extension = file.split('.')
        if extension == 'png':
            IMAGES[file_name] = pygame.image.load(
                os.path.join(path, file)
            ).convert_alpha()

# retrieving text files for tooltips
ITEM_TOOLTIPS = {}
for (path, dirs, files) in os.walk(ITEM_PATH, topdown=True):
    for file in files:
        with open(os.path.join(path, file), 'r') as item:
            tooltip = [line.strip() for line in item.readlines()]
            ITEM_TOOLTIPS[tooltip[0].replace(" ", "_").lower()] = tooltip

# "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0
# creating multiple font sizes
COMICORO = {}
font_sizes = (20, 25, 35, 50)
for size in font_sizes:
    COMICORO[size] = pygame.font.Font('../comicoro.ttf', size)


def randomize(value: int, offset: float):
    '''Randomizes the value with a +- deviation of the offset'''
    return random.randint(
        round(value * (1 - offset)),
        round(value * (1 + offset))
    )


def color_image(image: pygame.Surface, color: list, transparency=255):
    '''Recolors a surface'''
    image = image.copy()

    # zeros out rgb and preserves original transparency
    image.fill((0, 0, 0, 255), None, special_flags=pygame.BLEND_RGBA_MULT)

    # adds in new rgb values
    image.fill(color + (0,), None, pygame.BLEND_RGBA_ADD)

    if transparency:
        image.set_alpha(transparency)

    return image


def get_circle_surface(radius: float, color: list):
    '''Returns a circle surface'''
    circle_surface = pygame.Surface((radius * 2,) * 2, pygame.SRCALPHA)
    center = (radius,) * 2

    pygame.draw.circle(
        circle_surface,
        color,
        center,
        radius
    )

    return circle_surface
