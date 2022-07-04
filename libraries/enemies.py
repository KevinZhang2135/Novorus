import pygame
import math
import random

from libraries.tools import *

class Ghost(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size
        
        self.image = load_image('ghost_idle1.png', size)
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.in_combat = False
        self.attacking = False

        self.move_speed = 2
        self.ticks = random.randint(0, 30)
        self.level = random.randint(1, 2)

        self.facing = random.choice(['left', 'right'])
        self.name = 'Ghost'

        health = round(30 * (1.1**(self.level - 1)))
        self.health = {'current': health,
                       'total': health}

        attack = round(10 * (1.1**(self.level - 1)))
        self.attack = {'current': attack,
                       'total': attack}

        speed = round(15 * (1.1**(self.level - 1)))
        self.speed = {'current': speed,
                      'total': speed}

    def animation(self):
        '''Handles animation'''
        idle_sprites = ['ghost_idle1.png',
                        'ghost_idle2.png',
                        'ghost_idle3.png',
                        'ghost_idle2.png']

        combat_sprites = ['ghost_idle1.png',
                          'ghost_attack1.png',
                          'ghost_attack2.png',
                          'ghost_attack3.png']

        if not self.in_combat:
            self.image = load_image(
                idle_sprites[math.floor(self.ticks / 30)], 
                (self.width, self.height))

        else:
            if self.attacking:
                self.image = load_image(
                    combat_sprites[math.floor((self.ticks - 40) / 25)], 
                    (self.width, self.height))

            else:
                self.image = load_image(
                    idle_sprites[math.floor(self.ticks / 30)], 
                    (self.width, self.height))

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player, collision_group):
        '''Handles events'''
        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0