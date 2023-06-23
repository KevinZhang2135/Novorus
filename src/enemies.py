from constants import *
from effects import *
from entity import *

import pygame

class Ghost(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.show_stats = True
        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Ghost'

        # hitbox
        self.set_hitbox(0.4, 0.5)

        # movement
        self.detection_distance = 350
        self.max_velocity = 2

        # stats
        self.exp = 15
        self.exp_levels = None

        self.stats = Stats(3000, 10, 6, 0.05, 0.1)

        # general animation
        self.frame = 0
        self.animation_types = {
            'idle': [],
            'run': [],
            'attack': []
        }

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'{SPRITE_PATH}/enemies/ghost/{type}'
            ))

            for i in range(num_of_frames):
                image = IMAGES[f'ghost_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, 
                    size
                )

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

    def movement(self):
        '''Handles movement'''
        self.acceleration = pygame.math.Vector2(self.game.player.rect.centerx - self.rect.centerx,
                                                self.game.player.rect.centery - self.rect.centery)

        if (self.acceleration.length() < self.detection_distance
                and not self.attacking):
            if self.acceleration.length() > 0:
                self.acceleration.scale_to_length(self.max_velocity)

            self.velocity += self.acceleration
            self.velocity *= 0.5

        else:
            # movement decay
            self.velocity *= 0.8
            self.acceleration.x = 0
            self.acceleration.y = 0

        # movement decay when the speed is low
        if abs(self.velocity.x) < self.max_velocity / 10:
            self.velocity.x = 0

        if abs(self.velocity.y) < self.max_velocity / 10:
            self.velocity.y = 0

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

    def check_state(self):
        if not self.attacking:
            if self.velocity.length_squared() > 0:
                self.action = 'run'

                if self.velocity.x < 0:
                    self.facing = 'left'

                elif self.velocity.x > 0:
                    self.facing = 'right'

            else:
                self.action = 'idle'

        else:
            self.action = 'attack'

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.check_death()
        self.animation()


class Mimic(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Mimic'

        # stats
        self.exp = 50
        self.exp_levels = False

        self.stats = Stats(100, 20, 7, 0.15, 0)

        # animation
        self.frame = 0
        self.animation_types = {
            'idle': [],
            'attack': []
        }

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'{SPRITE_PATH}/enemies/mimic/{type}'
            ))

            for i in range(num_of_frames):
                image = IMAGES[f'mimic_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, 
                    size
                )

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])
        

        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

    def update(self):
        '''Handles events'''
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.check_death()
        self.animation()


class Sunflower(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Sunflower'

        # hitbox
        self.set_hitbox(0.4, 0.9)

        # stats
        self.exp = 5
        self.exp_levels = False

        self.stats = Stats(20, 5, 4, 0.05, 0)

        # general animation
        self.frame = 0
        self.animation_types = {
            'idle': [],
            'attack': []
        }

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'{SPRITE_PATH}/enemies/sunflower/{type}'
            ))

            for i in range(num_of_frames):
                image = IMAGES[f'sunflower_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, 
                    size
                )

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (1200 - self.stats.speed) \
            / len(self.animation_types['attack'])
        
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

    def update(self):
        '''Handles events'''
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.check_death()
        self.animation()
