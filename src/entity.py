from constants import *
from effects import *
from sprite import Sprite
from random import randint

import pygame
from math import dist


class Entity(Sprite):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.attacking = False
        self.show_stats = False

        self.stats = None

        # movement
        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.max_velocity = 0

        # render
        self.sprite_layer = 1

        self.animation_types = {}
        self.animation_cooldown = 0
        self.attack_cooldown = 0

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
                self, self.game.collision_group, False)
            sprites.sort(key=lambda sprite: dist(
                self.hitbox.center, sprite.hitbox.center))

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
        # checks if the player rect overlaps an enemy rect
        colliding_sprites = pygame.sprite.spritecollide(
                self,
                target_group,
                False
            )

        colliding_sprites.sort(
            key=lambda sprite: dist(
                self.hitbox.center, sprite.hitbox.center)
        )

        self.attacking = False
        self.cooldown = self.animation_cooldown

        for sprite in colliding_sprites:
            # checks if mask overlaps an enemy hitbox
            mask = pygame.mask.from_surface(self.image)
            offset = (sprite.hitbox.x - self.rect.x,
                      sprite.hitbox.y - self.rect.y)

            # when attacking, whole sprite is used as the mask for attack
            # damage is done to hitbox
            if mask.overlap(sprite.rect_mask, offset):
                self.attacking = True
                self.cooldown = self.attack_cooldown

                self.face_enemy(sprite)

                # only attacks the last frame
                if (pygame.time.get_ticks() - self.attack_time > self.attack_cooldown
                        and self.frame == len(self.animation_types['attack']) - 1):
                    
                    self.attack_time = pygame.time.get_ticks()
                    sprite.hurt(self.stats.attack, self.stats.crit_chance)

    def check_state(self):
        if self.attacking:
            self.action = 'attack'

        else:
            self.action = 'idle'

    def check_death(self):
        if self.stats.health < 0:
            # sprite dies
            self.stats.health = 0
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = self.game.player.animation_cooldown

            # creates dust particles on death
            for i in range(5):
                x_offset = round((self.rect.right - self.rect.left) / 4)
                x = randint(
                    self.rect.centerx - x_offset,
                    self.rect.centerx + x_offset
                )

                y_offset = round((self.rect.bottom - self.rect.top) / 4)
                y = randint(
                    self.rect.centery - y_offset,
                    self.rect.centery + y_offset
                )

                dust = Particle(
                    (x, y),
                    [randomize(self.rect.width / 2, 0.05) for i in range(2)],
                    self.game,
                    self.game.camera_group
                )

                dust.set_image(f'dust{random.randint(1, 3)}')
                dust.velocity.y = -2

            self.kill()
            del self

    def hurt(self, attack: int, crit_chance: float):
        text_coords = (
            random.randint(
                round((self.hitbox.left + self.hitbox.centerx) / 2),
                round((self.hitbox.right + self.hitbox.centerx) / 2)),
            self.hitbox.top)

        dodge = self.stats.dodge_chance >= random.randint(0, 100) / 100
        if not dodge:
            # randomizes damage between 0.9 and 1.1
            damage = randomize(attack, 0.15)

            # doubles damage if crit
            crit = crit_chance >= random.randint(0, 100) / 100
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

            else:
                text = TextPopUp(
                    text_coords, 
                    self.game,
                    self.game.camera_group
                )
                
                text.set_text(COMICORO[25].render(str(damage), True, RED))
                text.velocity.y = -5

            self.stats.health -= damage

        else:
            text = TextPopUp(text_coords, self.game, self.game.camera_group)
            text.set_text(COMICORO[20].render('Dodged', True, GOLD))
            text.velocity.y = -5

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
