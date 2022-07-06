import pygame
import math

from libraries.tools import *


class Player(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(groups)
        self.width, self.height = size

        self.image = load_image('knight_walk1.png', size)
        self.rect = self.image.get_rect(center=coords)
        self.mask = pygame.mask.from_surface(self.image)

        self.colliding = False
        self.in_combat = False
        self.attacking = False

        self.facing = 'right'
        self.name = 'Player'

        self.bonuses = {'health': 0,
                         'speed': 0,
                         'attack': 0}

        self.health = {'current': 100,
                       'total': 100,
                       'base': 100}

        self.speed = {'current': 30,
                      'total': 30,
                      'base': 30}

        self.attack = {'current': 20,
                       'total': 20,
                       'base': 20}
        
        self.move_speed = 5
        self.ticks = 0
        self._level = 1
        self.set_stats()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value
        self.set_stats()
    
    def set_stats(self):
        stats = {'health': self.health,
                 'speed': self.speed,
                 'attack': self.attack}

        for type in stats:
            ratio = stats[type]['current'] / stats[type]['total']
            
            stats[type]['total'] = round(stats[type]['base']
                                        * (1 + self.bonuses[type])
                                        * (1.05**(self._level - 1)))

            stats[type]['current'] = round(ratio * stats[type]['total'])

    def movement(self):
        '''Handles movement'''
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        up = keys[pygame.K_UP] or keys[pygame.K_w]

        # creates movement using falsy and truthy values that evaluate to 0 and 1
        move = pygame.math.Vector2(right - left, down - up)
        if move.length_squared() > 0:  # checks if the player is moving
            # converts the coordinates to a vector according to the radius
            move.scale_to_length(self.move_speed)

        if not self.in_combat:
            self.rect.centerx += move.x
            self.rect.centery += move.y

    def collision(self, sprites):
        '''Handles collision'''
        for sprite in sprites:
            collision_distance = pygame.math.Vector2((self.rect.width + sprite.rect.width) / 2,
                                                     (self.rect.height + sprite.rect.height) / 2)

            distance = pygame.math.Vector2(self.rect.centerx - sprite.rect.centerx,
                                           self.rect.centery - sprite.rect.centery)

            # checks if the distance of the sprites are within collision distance
            if (abs(distance.x) + self.width / 6 < collision_distance.x
                    and abs(distance.y) + self.height / 6 < collision_distance.y):

                # horizontal collision
                if abs(distance.x) > abs(distance.y):
                    # left collision
                    if distance.x > 0:
                        self.rect.left = sprite.rect.right - self.width / 6

                    # right collision
                    if distance.x < 0:
                        self.rect.right = sprite.rect.left + self.width / 6

                # vertical collision
                elif abs(distance.y) > abs(distance.x):
                    # bottom collision
                    if distance.y < 0:
                        self.rect.bottom = sprite.rect.top + self.height / 6

                    # top collision
                    if distance.y > 0:
                        self.rect.top = sprite.rect.bottom - self.height / 6

    def animation(self):
        '''Handles animation'''
        movement_sprites = ['knight_walk1.png',
                            'knight_walk2.png',
                            'knight_walk1.png',
                            'knight_walk3.png']

        idle_sprites = ['knight_walk1.png',
                        'knight_idle1.png',
                        'knight_walk1.png',
                        'knight_idle2.png']

        combat_sprites = ['knight_walk1.png',
                          'knight_attack1.png',
                          'knight_attack2.png',
                          'knight_attack3.png']

        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            if left or right or down or up:
                self.image = load_image(
                    movement_sprites[math.floor(self.ticks / 30)],
                    (self.width, self.height))

                if left:
                    self.facing = 'left'

                elif right:
                    self.facing = 'right'

            else:
                self.image = load_image(
                    idle_sprites[math.floor(self.ticks / 30)],
                    (self.width, self.height))

        else:
            if self.attacking:
                self.image = load_image(
                    combat_sprites[math.floor((self.ticks - 20) / 25)],
                    (self.width, self.height))

            else:
                self.image = load_image(
                    idle_sprites[math.floor(self.ticks / 30)],
                    (self.width, self.height))

        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player, collision_group):
        '''Handles events'''
        self.movement()
        self.collision(collision_group)
        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
