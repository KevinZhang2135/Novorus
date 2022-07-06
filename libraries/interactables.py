import pygame

from libraries.tools import *


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image('chest_closed.png', size)
        self.rect = self.image.get_rect(center=coords)

        self.opened = False

    def collision(self, player):
        collision_distance = pygame.math.Vector2((self.rect.width + player.rect.width) / 2,
                                                 (self.rect.height + player.rect.height) / 2)

        distance = pygame.math.Vector2(self.rect.centerx - player.rect.centerx,
                                       self.rect.centery - player.rect.centery)

        # checks if the distance of the sprites are within collision distance
        if (abs(distance.x) - 1 < collision_distance.x
            and abs(distance.y) - 1 < collision_distance.y
            and not self.opened):

            self.image = load_image(
                'chest_opened.png',
                (self.width, self.height))

            self.opened = True
            player.bonuses['attack'] += 1
            player.set_stats()

    def update(self, player, collision_group):
        self.collision(player)
