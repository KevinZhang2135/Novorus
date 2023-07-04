from constants import *

import pygame

class Shadow:
    def __init__(self, color, points):
        x, y = zip(*points)

        # determines bounds of rect
        min_x, min_y, max_x, max_y = min(x), min(y), max(x), max(y)

        # draws polygon onto surface for color
        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        mask = pygame.Surface(target_rect.size, pygame.SRCALPHA)

        pygame.draw.polygon(mask, color, [(x - min_x, y - min_y) for x, y in points])