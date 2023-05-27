from effects import *
from sprite import Sprite
from random import randint

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
                            self.set_coords(sprite.rect.right + self.rect.width / 2, self.coords.y)

                        # right collision
                        elif center_distance.x < 0:
                            self.set_coords(sprite.rect.left - self.rect.width / 2, self.coords.y)

                        self.velocity.x = 0

                    # vertical collision
                    elif (abs(center_distance.y) > abs(center_distance.x)):
                        # bottom collision
                        if center_distance.y < 0:
                            self.set_coords(self.coords.x, sprite.rect.top - self.rect.height / 2)

                        # top collision
                        elif center_distance.y > 0:
                            self.set_coords(self.coords.x, sprite.rect.bottom + self.rect.height / 2)

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
                x = randint(
                    self.rect.centerx - x_offset,
                    self.rect.centerx + x_offset)

                y_offset = round((self.rect.bottom - self.rect.top) / 4)
                y = randint(
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

                text = TextPopUp(text_coords, self.game, self.game.camera_group)
                text.set_text(COMICORO[35].render(str(damage), True, BLOOD_RED))
                text.velocity.y = -5

            else:
                text = TextPopUp(text_coords, self.game, self.game.camera_group)
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


