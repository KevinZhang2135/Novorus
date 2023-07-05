from constants import *

import pygame
import math

class Shadow:
    def __init__(self, color, image):
        points = []
        for x, y in pygame.mask.from_surface(image).outline(every=2):
            shadow_height = y * 0.2
            shadow_width = shadow_height * math.tan(math.pi * 2 / 3)
            points.append((x + shadow_width, y + shadow_height))

        x, y = zip(*points)

        # determines bounds of rect
        min_x, min_y, max_x, max_y = min(x), min(y), max(x), max(y)

        # draws polygon onto surface for color
        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        self.surface = pygame.Surface(target_rect.size, pygame.SRCALPHA)

        if len(points) > 2:
            pygame.draw.polygon(self.surface, color, [(x - min_x, y - min_y) for x, y in points])

    