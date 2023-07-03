import pygame
import os
import random

pygame.init()
pygame.display.set_mode()

# colors
RED = (211, 47, 47)
BLOOD_RED = (198, 40, 40)

ORANGE = (255, 174, 66)
TANGERINE = (212, 103, 0)

MELLOW_YELLOW = (255, 229, 134)
YELLOW = (255, 231, 45)
GOLD = (241, 205, 0)

SLATE_BLUE = (100, 117, 128)

WHITE = (255, 255, 255)
LIGHT_GREY = (210, 210, 210)
GREY = (188, 188, 188)
DARK_GREY = (168, 168, 168)
BLACK = (50, 50, 50)
MIDNIGHT = (0, 0, 0)

BROWN = (131, 106, 83)
PECAN = (115, 93, 71)
DARK_BROWN = (104, 84, 66)

# tile pixel size
TILE_SIZE = 100
STARTING_FLOOR = 2

# file paths
LEVEL_PATH = '../levels'
SPRITE_PATH = '../sprites'
ITEM_PATH = '../items'

# retrieving image files for tooltips
IMAGES = {}
for (path, dirs, files) in os.walk(SPRITE_PATH, topdown=True):
    for file in files:
        IMAGES[file[:-4]] = pygame.image.load(
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


def color_image(image: pygame.Surface, color: list, transparency: int = 255):
    '''Recolors a surface'''
    image = image.copy()

    # zeros out rgb and preserves original transparency
    image.fill((0, 0, 0, 255), None, special_flags=pygame.BLEND_RGBA_MULT)

    # adds in new rgb values
    image.fill(color + (0,), None, pygame.BLEND_RGBA_ADD)

    if transparency:
        image.set_alpha(transparency)

    return image


