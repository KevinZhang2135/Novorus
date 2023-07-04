from constants import *
from particles import *
from sprite import Sprite

import pygame
from math import dist
from random import randint


class Stats:
    def __init__(self, health: int, speed: int, attack: int, crit_chance: float, dodge_chance: float):
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


class Entity(Sprite):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.name = ''
        self.action = 'idle'
        self.facing = random.choice(('left', 'right'))

        self.attacking = False
        self.in_combat = False
        self.show_stats = True

        self.stats = None

        # movement
        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.max_velocity = 0

        # render
        self.sprite_layer = 3

        # animation
        self.frame = 0
        self.cooldown = 0
        self.loop_frames = True

        self.attack_cooldown = 0
        self.attack_time = pygame.time.get_ticks()

        self.animation_cooldown = 0
        self.animation_time = pygame.time.get_ticks()
        self.animation_frames = {
            'idle': [],
            'run': [],
            'attack': []
        }


    def set_animation(self, filepath: str):
        unused_types = []
        for type in self.animation_frames:
            path = f'{SPRITE_PATH}/{filepath}/{type}'
            if os.path.exists(path):
                for path in os.listdir(path):
                    image = IMAGES[path[:-4]].copy()
                    image = pygame.transform.scale(
                        image,
                        self.rect.size
                    )

                    self.animation_frames[type].append(image)

            else:
                unused_types.append(type)

        # cleans unused types
        for type in unused_types:
            del self.animation_frames[type]

        # sets image
        self.image = self.animation_frames[self.action][self.frame]

    def line_of_sight(self, point):
        distance = dist(self.hitbox.center, point)

        # filters walls beyond point
        walls = [
            wall for wall in self.game.collision_group.sprites()
            if dist(self.hitbox.center, wall.hitbox.center) < distance
        ]

        for wall in walls:
            if wall.hitbox.clipline(self.hitbox.center, point):
                return False

        return True

    def movement(self):
        '''Handles movement'''

        # movement decay when the speed is low
        if abs(self.velocity.x) < self.max_velocity / 10:
            self.velocity.x = 0

        if abs(self.velocity.y) < self.max_velocity / 10:
            self.velocity.y = 0

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

    def collision(self):
        '''Handles collision'''
        if abs(self.velocity.x) > 0 or abs(self.velocity.y) > 0:
            # sorts sprites by distance
            sprites = pygame.sprite.spritecollide(
                self,
                self.game.collision_group,
                False
            )

            sprites.sort(key=lambda sprite: dist(
                self.hitbox.center,
                sprite.hitbox.center
            ))

            for sprite in sprites:
                # minimum distance between two sprites which includes collision
                collision_distance = pygame.math.Vector2(
                    (self.hitbox.width + sprite.hitbox.width) / 2,
                    (self.hitbox.height + sprite.hitbox.height) / 2
                )

                # distance between the centers of two sprites
                center_distance = pygame.math.Vector2(
                    self.hitbox.centerx - sprite.hitbox.centerx,
                    self.hitbox.centery - sprite.hitbox.centery
                )

                # checks if the distance of the sprites are within collision distance
                if (abs(center_distance.x) < collision_distance.x
                        and abs(center_distance.y) < collision_distance.y):
                    # horizontal collision
                    if (abs(center_distance.x) > abs(center_distance.y)):
                        # left collision
                        if center_distance.x > 0:
                            self.set_coords(
                                sprite.hitbox.right + self.hitbox.width / 2 - self.hitbox_offset.x + 1,
                                self.coords.y
                            )

                        # right collision
                        elif center_distance.x < 0:
                            self.set_coords(
                                sprite.hitbox.left - self.hitbox.width / 2 - self.hitbox_offset.x - 1,
                                self.coords.y
                            )

                        self.velocity.x = 0

                    # vertical collision
                    else:
                        # top collision
                        if center_distance.y > 0:
                            self.set_coords(
                                self.coords.x,
                                sprite.hitbox.bottom + self.hitbox.height / 2 - self.hitbox_offset.y + 1
                            )

                        # bottom collision
                        elif center_distance.y < 0:
                            self.set_coords(
                                self.coords.x,
                                sprite.hitbox.top - self.hitbox.height / 2 - self.hitbox_offset.y - 1
                            )

                        self.velocity.y = 0

            screen_left = TILE_SIZE / 2
            screen_right = self.game.level.rect.right - TILE_SIZE / 2
            screen_top = -TILE_SIZE / 2
            screen_bottom = self.game.level.rect.bottom - TILE_SIZE / 2

            # left edge map
            if self.hitbox.left < screen_left:
                self.velocity.x = 0
                self.set_coords(
                    self.hitbox.width / 2 + screen_left - self.hitbox_offset.x + 1,
                    self.coords.y
                )

            # right edge map
            elif self.hitbox.right > screen_right:
                self.velocity.x = 0
                self.set_coords(
                    screen_right - self.hitbox.width / 2 - self.hitbox_offset.x - 1,
                    self.coords.y
                )

            # top edge map
            if self.hitbox.top < screen_top:
                self.velocity.y = 0
                self.set_coords(
                    self.coords.x,
                    screen_top + self.hitbox.height / 2 - self.hitbox_offset.y + 1
                )

            # bottom edge map
            elif self.hitbox.bottom > screen_bottom:
                self.velocity.y = 0
                self.set_coords(
                    self.coords.x,
                    screen_bottom - self.hitbox.height / 2 - self.hitbox_offset.y - 1
                )

    def face_enemy(self, target: Sprite):
        if self.hitbox.centerx < target.hitbox.centerx:
            self.facing = 'right'

        else:
            self.facing = 'left'

    def attack_enemy(self, target_group: pygame.sprite.Group):
        pass

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

        if not self.animation_frames[self.action]:
            self.action = 'idle'

    def check_death(self):
        if self.stats.health <= 0:
            # sprite dies
            self.stats.health = 0

            # creates dust particles on death
            for i in range(5):
                x_offset = round((self.hitbox.right - self.hitbox.left) / 4)
                x = randint(
                    self.hitbox.centerx - x_offset,
                    self.hitbox.centerx + x_offset
                )

                y_offset = round((self.hitbox.bottom - self.hitbox.top) / 4)
                y = randint(
                    self.hitbox.centery - y_offset,
                    self.hitbox.centery + y_offset
                )

                Dust(
                    (x, y),
                    [randomize(self.hitbox.width / 2, 0.05) for i in range(2)],
                    self.game,
                    self.game.camera_group
                )

            self.kill()
            del self

    def hurt(self, stats):
        text_coords = (
            random.randint(
                round((self.hitbox.left + self.hitbox.centerx) / 2),
                round((self.hitbox.right + self.hitbox.centerx) / 2)
            ),
            self.hitbox.top
        )

        dodge = self.stats.dodge_chance > random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(stats.attack, 0.15)

            # doubles damage if crit
            crit = stats.crit_chance >= random.randint(0, 100) / 100
            if crit:
                damage *= 2

                text = TextPopUp(
                    text_coords,
                    self.game,
                    self.game.camera_group
                )

                text.set_text(COMICORO[35].render(
                    str(damage), True, BLOOD_RED)
                )

                text.velocity.y = -5

            # non-crit damage
            else:
                text = TextPopUp(
                    text_coords,
                    self.game,
                    self.game.camera_group
                )

                text.set_text(COMICORO[25].render(str(damage), True, RED))
                text.velocity.y = -5

            self.stats.health -= damage

        # damage is dodged
        else:
            text = TextPopUp(text_coords, self.game, self.game.camera_group)
            text.set_text(COMICORO[20].render('Dodged', True, GOLD))
            text.velocity.y = -5

    def animation(self):
        '''Handles animation'''

        # loops frames
        if self.frame >= len(self.animation_frames[self.action]) and self.loop_frames:
            self.frame = 0

        # set image
        if self.frame < len(self.animation_frames[self.action]):
            self.image = self.animation_frames[self.action][self.frame]

            # determines whether the animation cooldown is over
            if pygame.time.get_ticks() - self.animation_time > self.cooldown:
                self.animation_time = pygame.time.get_ticks()
                self.frame += 1

            # reflects over y-axis if facing left
            if self.facing == 'left':
                self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.check_death()
        self.animation()


class MeleeEnemy(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        # movement
        self.detection_distance = 0
        self.max_velocity = 0

    def movement(self):
        '''Handles movement'''
        self.acceleration = pygame.math.Vector2(
            self.game.player.rect.centerx - self.rect.centerx,
            self.game.player.rect.centery - self.rect.centery
        )

        line_of_sight = self.line_of_sight(self.game.player.hitbox.center)

        # if target within detection range and line of sight
        if (self.acceleration.length() < self.detection_distance
                and not self.in_combat
                and line_of_sight):

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
        super().movement()

    def attack_enemy(self, target_group: pygame.sprite.Group):
        # checks if the rect overlaps an enemy rect
        self.in_combat = False
        colliding_sprites = pygame.sprite.spritecollide(
            self,
            target_group,
            False
        )

        # sorts sprites by distance
        colliding_sprites.sort(key=lambda sprite: dist(
            self.hitbox.center,
            sprite.hitbox.center
        ))

        targets_hit = []
        for sprite in colliding_sprites:
            # checks if mask overlaps an enemy hitbox
            mask = pygame.mask.from_surface(self.image)
            offset = (
                sprite.hitbox.x - self.rect.x,
                sprite.hitbox.y - self.rect.y
            )

            # when attacking, whole sprite is used as the mask for attack
            # damage is done to hitbox
            if mask.overlap(sprite.rect_mask, offset):
                # trigger attack animation
                self.in_combat = True
                self.show_stats = True
                if not self.attacking:
                    self.frame = 0
                    self.attacking = True
                    self.cooldown = self.attack_cooldown

                self.face_enemy(sprite)

                # only attacks the last frame
                if (pygame.time.get_ticks() - self.attack_time > self.attack_cooldown
                        and self.frame == len(self.animation_frames['attack'])
                        and sprite not in targets_hit):

                    sprite.hurt(self.stats)
                    targets_hit.append(sprite)

        if targets_hit:
            self.attack_time = pygame.time.get_ticks()

        # clear attack animation if not in combat
        if not self.in_combat:
            self.attacking = False
            self.cooldown = self.animation_cooldown


class RangerEnemy(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        # movement
        self.detection_distance = 0
        self.max_velocity = 0

        # attack
        self.attack_range = 0

    def movement(self):
        self.acceleration = pygame.math.Vector2(
            self.game.player.rect.centerx - self.rect.centerx,
            self.game.player.rect.centery - self.rect.centery
        )

        player_distance = dist(
            self.hitbox.center,
            self.game.player.hitbox.center
        )

        line_of_sight = self.line_of_sight(self.game.player.hitbox.center)

        # if target within detection range and line of sight
        if (self.acceleration.length() < self.detection_distance
                and player_distance > self.attack_range
                and not self.attacking
                and line_of_sight):

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
        super().movement()

    def attack_enemy(self, target_group: pygame.sprite.Group):
        # checks if the target rect is within attack range
        targets = target_group.sprites()
        targets.sort(key=lambda sprite: dist(
            self.hitbox.center,
            sprite.hitbox.center
        ))

        # attacks when target is within attack range
        if (len(targets) > 0
                and dist(self.hitbox.center, targets[0].hitbox.center) < self.attack_range
                and self.line_of_sight(targets[0].hitbox.center)):

            self.in_combat = True
            self.cooldown = self.attack_cooldown

            self.face_enemy(targets[0])

            # only attacks the last frame
            if (pygame.time.get_ticks() - self.attack_time > self.attack_cooldown):
                # trigger attack animation
                if not self.attacking:
                    self.frame = 0
                    self.attacking = True

                # shoot projectile after animation ends
                if (self.frame == len(self.animation_frames['attack'])):
                    self.attack_time = pygame.time.get_ticks()
                    self.attacking = False

                    self.create_projectile(targets[0])

        # cancels attack when target moves outside attack range
        else:
            self.attacking = False
            self.in_combat = False
            self.cooldown = self.animation_cooldown

    def create_projectile(self, target):
        pass
