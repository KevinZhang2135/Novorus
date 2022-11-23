import os, pygame

# colors
RED = (211, 47, 47)
BLOOD_RED = (198, 40, 40)

ORANGE = (255, 174, 66)
TANGERINE = (212, 103, 0)

MELLOW_YELLOW = (255, 229, 134)
YELLOW = (255, 231, 45)
GOLD = (255, 219, 14)

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

TILE_SIZE = 100
STARTING_FLOOR = 1
game_state = {'unpaused': True,
              'runtime': True,
              'fullscreen': True}

IMAGES = {}
for (path, dirs, files) in os.walk('./sprites', topdown=True):
    for file in files:
        IMAGES[file] = path

for file, path in IMAGES.items():
    IMAGES[file] = pygame.image.load(os.path.join(path, file)).convert_alpha()

# "Creative Commons Comicoro" by jeti is licensed under CC BY 4.0
COMICORO = {}
font_sizes = (20, 25, 35, 50)
for size in font_sizes:
    COMICORO[size] = pygame.font.Font('./comicoro.ttf', size)

