from constants import *

import pygame


class Shadow:
    def __init__(self, color, image):
        points = []
        mask_outline = pygame.mask.from_surface(image).outline(every=1)

        for x, y in mask_outline:
            shadow_height = (image.get_height() - y) * 0.5
            shadow_width = shadow_height * math.tan(math.pi / 3)
            points.append((x + shadow_width, y + shadow_height))

        # zips coords into its separate x's and y's
        x, y = zip(*points)

        # determines bounds of rect
        min_x, min_y, max_x, max_y = min(x), min(y), max(x), max(y)

        # draws polygon onto surface for color
        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        self.surface = pygame.Surface(target_rect.size, pygame.SRCALPHA)

        if len(points) > 2:
            pygame.draw.polygon(
                self.surface, 
                color, 
                [(x - min_x, y - min_y) for x, y in points]
            )

        self.surface.convert_alpha()