from constants import *
from effects import *
from entity import *


class Ghost(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.show_stats = True
        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Ghost'

        # movement
        self.detection_distance = 350
        self.max_velocity = 2

        # stats
        self.exp = 15
        self.exp_levels = None

        self.stats = Stats(30, 10, 6, 0.05, 0.1)

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'run': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'{SPRITE_PATH}/enemies/ghost/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'ghost_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, size)

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (
            1200 - self.stats.speed) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

    def check_state(self):
        if not self.in_combat:
            if self.velocity.length_squared() > 0:
                self.action = 'run'

                if self.velocity.x < 0:
                    self.facing = 'left'

                elif self.velocity.x > 0:
                    self.facing = 'right'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            else:
                self.action = 'idle'

        if self.stats.health < 0:
            # sprite dies
            self.stats.health = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = self.game.player.animation_cooldown

            for i in range(5):
                x_offset = round((self.rect.right - self.rect.left) / 4)
                x = random.randint(
                    self.rect.centerx - x_offset,
                    self.rect.centerx + x_offset)

                y_offset = round((self.rect.bottom - self.rect.top) / 4)
                y = random.randint(
                    self.rect.centery - y_offset,
                    self.rect.centery + y_offset)

                dust = Particle(
                    (x, y),
                    [randomize(self.rect.width / 2, 0.05) for i in range(2)],
                    self.game,
                    self.game.camera_group)

                dust.set_image(f'dust{random.randint(1, 3)}')
                dust.velocity.y = -2

            self.kill()
            del self

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.animation()


class Mimic(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Mimic'

        # stats
        self.exp = 50
        self.exp_levels = False

        self.stats = Stats(100, 20, 7, 0.15, 0)

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'{SPRITE_PATH}/enemies/mimic/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'mimic_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, size)

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (
            1200 - self.stats.speed) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

    def update(self):
        '''Handles events'''
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.animation()


class Sunflower(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))
        self.name = 'Sunflower'

        # stats
        self.exp = 5
        self.exp_levels = False

        self.stats = Stats(20, 5, 4, 0.05, 0)

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(
                f'{SPRITE_PATH}/enemies/sunflower/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'sunflower_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, size)

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1600 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (
            1200 - self.stats.speed) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

    def update(self):
        '''Handles events'''
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.animation()
