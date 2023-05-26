from constants import *
from effects import *
from ui import Inventory
from sprite import Sprite

import pygame


class Entity(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.in_combat = False
        self.attacking = False
        self.show_stats = False

        self.stats = None

        # movement
        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.max_velocity = 0

        # render
        self.mask = pygame.mask.from_surface(self.image)
        self.sprite_layer = 1

    def movement(self):
        '''Handles movement'''
        self.acceleration = pygame.math.Vector2(self.game.player.rect.centerx - self.rect.centerx,
                                                self.game.player.rect.centery - self.rect.centery)

        if (self.acceleration.length() < self.detection_distance
                and not self.in_combat):
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
            self.coords.y + self.velocity.y)

    def collision(self):
        '''Handles collision'''
        if abs(self.velocity.x) > 0 or abs(self.velocity.y) > 0:
            for sprite in self.game.collision_group:
                collision_distance = pygame.math.Vector2((self.rect.width + sprite.rect.width) / 2,
                                                         (self.rect.height + sprite.rect.height) / 2)

                center_distance = pygame.math.Vector2(self.rect.centerx - sprite.rect.centerx,
                                                      self.rect.centery - sprite.rect.centery)

                # checks if the distance of the sprites are within collision distance
                if (abs(center_distance.x) < collision_distance.x
                        and abs(center_distance.y) < collision_distance.y):

                    # horizontal collision
                    if (abs(center_distance.x) > abs(center_distance.y)):
                        # left collision
                        if center_distance.x > 0:
                            self.set_coords(sprite.rect.right + self.rect.width, self.coords.y)

                        # right collision
                        elif center_distance.x < 0:
                            self.set_coords(sprite.rect.left - self.rect.width, self.coords.y)

                        self.velocity.x = 0

                    # vertical collision
                    elif (abs(center_distance.y) > abs(center_distance.x)):
                        # bottom collision
                        if center_distance.y < 0:
                            self.set_coords(self.coords.x, sprite.rect.top - self.rect.height)

                        # top collision
                        elif center_distance.y > 0:
                            self.set_coords(self.coords.x, sprite.rect.bottom + self.rect.height)

                        self.velocity.y = 0

            # left edge map
            if self.rect.left < TILE_SIZE / 2:
                self.rect.left = TILE_SIZE / 2
                self.coords[0] = self.rect.centerx
                self.velocity.x = 0

            # right edge map
            elif self.rect.right > self.game.level.rect.right - TILE_SIZE / 2:
                self.rect.right = self.game.level.rect.right - TILE_SIZE / 2
                self.coords[0] = self.rect.centerx
                self.velocity.x = 0

            # top edge map
            if self.rect.top < -TILE_SIZE / 2:
                self.rect.top = -TILE_SIZE / 2
                self.coords[1] = self.rect.centery
                self.velocity.y = 0

            # bottom edge map
            elif self.rect.bottom > self.game.level.rect.bottom - TILE_SIZE / 2:
                self.rect.bottom = self.game.level.rect.bottom - TILE_SIZE / 2
                self.coords[1] = self.rect.centery
                self.velocity.y = 0

    def face_enemy(self, target):
        if self.rect.centerx < target.rect.centerx:
            self.facing = 'right'

        else:
            self.facing = 'left'

    def attack_enemy(self, target_group):
        # checks if the player mask overlaps an enemy mask
        if (pygame.sprite.spritecollide(self, target_group, False)
            and pygame.sprite.spritecollide(self, target_group, False, pygame.sprite.collide_mask)
                and self.stats.health > 0):

            distance = pygame.math.Vector2(self.rect.center)
            enemies = target_group.sprites()
            enemy = sorted(enemies, key=lambda enemy: distance.distance_to(
                enemy.rect.center))[0]  # closest enemy

            self.face_enemy(enemy)

            if not self.in_combat and enemy.stats.health > 0:
                self.in_combat = True
                self.show_stats = True
                self.animation_time = pygame.time.get_ticks()
                self.cooldown = self.attack_cooldown
                self.frame = 0

            if self.in_combat:
                if not self.attacking and pygame.time.get_ticks() - self.animation_time > self.cooldown:
                    self.attacking = True
                    self.frame = 0

                # only deal damage when animation ends
                if self.attacking and self.frame >= len(self.animation_types[self.action]) - 1:
                    if pygame.time.get_ticks() - self.animation_time > self.cooldown:
                        enemy.hurt(self.stats.attack,
                                   self.stats.crit_chance)

                        # gains exp if player is victorious
                        if enemy.stats.health <= 0:
                            self.in_combat = False
                            self.exp += enemy.exp
        else:
            self.in_combat = False
            self.attacking = False
            self.cooldown = self.animation_cooldown

    def check_state(self):
        if not self.in_combat:
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
                    f'dust{random.randint(1, 3)}',
                    self.game.camera_group)

                dust.velocity.y = -2

            self.kill()
            del self

    def hurt(self, attack, crit_chance):
        text_coords = (
            random.randint(
                round((self.rect.left + self.rect.centerx) / 2),
                round((self.rect.right + self.rect.centerx) / 2)),
            self.rect.top)

        dodge = self.stats.dodge_chance >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2

                text = COMICORO[35].render(str(damage), True, BLOOD_RED)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                self.game.camera_group.texts.append(text)

            else:
                text = COMICORO[25].render(str(damage), True, RED)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                self.game.camera_group.texts.append(text)

            self.stats.health -= damage

        else:
            text = COMICORO[20].render('Dodged', True, GOLD)
            text_rect = text.get_rect(center=text_coords)
            text = TextPopUp(text, text_rect)
            text.velocity.y = -5

            self.game.camera_group.texts.append(text)

    def animation(self):
        '''Handles animation'''
        # loops frames
        if self.frame >= len(self.animation_types[self.action]):
            self.frame = 0

        # set image
        self.image = self.animation_types[self.action][self.frame]

        # determines whether the animation cooldown is over
        if pygame.time.get_ticks() - self.animation_time > self.cooldown:
            self.animation_time = pygame.time.get_ticks()
            self.frame += 1

        # reflects over y-axis if facing left
        if self.facing == 'left':
            self.image = pygame.transform.flip(self.image, True, False)


class Stats:
    def __init__(self, health, speed, attack, crit_chance, dodge_chance):
        self.health = self.base_health = health
        self.speed = self.base_speed = speed
        self.attack = self.base_attack = attack

        self.base_crit_chance = crit_chance
        self.crit_chance = round(self.base_crit_chance + self.speed / 500, 2)
        if self.crit_chance > 0.5:
            self.crit_chance = 0.5

        self.base_dodge_chance = dodge_chance
        self.dodge_chance = round(self.base_dodge_chance + self.speed / 750, 2)
        if self.dodge_chance > 0.33:
            self.dodge_chance = 0.33


class Player(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        self.show_stats = True
        self.action = 'idle'
        self.facing = 'right'
        self.name = 'Player'

        # movement
        self.max_velocity = 15

        # stats
        self.exp = 0  # max exp is 9900
        self.exp_levels = [i for i in range(100, 10000, 100)]
        self.level = 1
        while self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

        self.stats = Stats(100, 10, 20, 0.05, 0.01)

        # sprites
        self.frame = 0
        self.animation_types = {'idle': [],
                                'run': [],
                                'attack': []}

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'{SPRITE_PATH}/player/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'knight_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image, size)

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1200 / len(self.animation_types['idle'])

        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (
            1200 - self.stats.speed) / len(self.animation_types['attack'])
        if self.attack_cooldown < 200:
            self.attack_cooldown = 200

        self.cooldown = self.animation_cooldown

        self.inventory = Inventory(ITEM_TOOLTIPS, self.game)
        self.inventory.add_item('wood_sword', 1)

        self.light_size = pygame.math.Vector2(700, 700)

        self.light = IMAGES['soft_circle'].copy()
        self.light = pygame.transform.scale(
            self.light, [int(dimension) for dimension in self.light_size])
        self.light = color_image(self.light, LIGHT_GREY, transparency=255)

    def movement(self):
        '''Handles movement'''
        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            # creates movement using falsy and truthy values that evaluate to 0 and 1
            self.acceleration = pygame.math.Vector2(right - left, down - up)
            if self.acceleration.length_squared() > 0:  # checks if the player is moving
                # converts the coordinates to a vector according to the radius
                self.acceleration.scale_to_length(self.max_velocity)
                self.velocity += self.acceleration
                self.velocity *= 0.5

            else:
                # movement decay when input is not received
                self.velocity *= 0.8
                self.acceleration.x = 0
                self.acceleration.y = 0

            # movement decay when the speed is low
            if abs(self.velocity.x) < self.max_velocity / 100:
                self.velocity.x = 0

            if abs(self.velocity.y) < self.max_velocity / 100:
                self.velocity.y = 0

            self.set_coords(
                self.coords.x + self.velocity.x,
                self.coords.y + self.velocity.y)

    def leveling_up(self):
        '''Increases player level when they reach exp cap'''
        if self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

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

    def hurt(self, attack, crit_chance):
        text_coords = (
            random.randint(
                round((self.rect.left + self.rect.centerx) / 2),
                round((self.rect.right + self.rect.centerx) / 2)),
            self.rect.top)

        dodge = self.stats.dodge_chance >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2

                text = COMICORO[35].render(str(damage), True, ORANGE)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                self.game.camera_group.texts.append(text)

            else:
                text = COMICORO[25].render(str(damage), True, TANGERINE)
                text_rect = text.get_rect(center=text_coords)
                text = TextPopUp(text, text_rect)
                text.velocity.y = -5

                self.game.camera_group.texts.append(text)

            self.stats.health -= damage

        else:
            text = COMICORO[20].render('Dodged', True, GOLD)
            text_rect = text.get_rect(center=text_coords)
            text = TextPopUp(text, text_rect)
            text.velocity.y = -5

            self.game.camera_group.texts.append(text)

        if self.stats.health < 0:
            # sprite dies
            self.stats.health = 0
            self.in_combat = False
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = self.game.player.animation_cooldown

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.enemy_group)
        self.check_state()
        self.animation()
        self.leveling_up()


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
                    f'dust{random.randint(1, 3)}',
                    self.game.camera_group)

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
