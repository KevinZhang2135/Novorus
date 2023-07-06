from ui import *
from particles import *
from projectiles import *

import pygame
import math


class Player(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.name = 'Player'
        self.facing = 'right'
        self.actions = ['idle', 'run', 'attack', 'charge']

        # hitbox
        self.set_hitbox(0.15, 0.3)

        # movement
        self.max_velocity = 5

        # stats
        self.exp = 0
        self.stats = Stats(100, 50, 20, 0.05, 0.01)

        # general animation
        self.animation_frames = {
            'left': {},
            'right': {}
        }

        self.set_animation('player', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}

        self.animation_cooldowns['idle'] = 1500 / \
            len(self.animation_frames[self.facing]['idle'])

        self.animation_cooldowns['run'] = self.animation_cooldowns['idle']
        self.animation_cooldowns['attack'] = (700 - self.stats.speed) \
            / len(self.animation_frames[self.facing]['attack'])

        if self.animation_cooldowns['attack'] < 50:
            self.animation_cooldowns['attack'] = 50

        self.animation_cooldowns['charge'] = self.animation_cooldowns['idle']

        self.animation_cooldown = self.animation_cooldowns[self.action]

        # attack cooldown
        self.attack_cooldown = self.animation_cooldowns['attack']

        # charge
        self.charging = False
        self.charge_cooldown = 2000

        # inventory
        self.inventory = Inventory(ITEM_TOOLTIPS, self.game)

    def movement(self):
        '''Handles movement'''
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        up = keys[pygame.K_UP] or keys[pygame.K_w]

        # creates movement using falsy and truthy values that evaluate to 0 and 1
        self.acceleration = pygame.math.Vector2(right - left, down - up)
        if not self.attacking and self.acceleration.length_squared() > 0:  # checks if the player is moving
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
        super().movement()

    def attack_enemy(self, target_group: pygame.sprite.Group):
        self.in_combat = False

        # attacks in a circular swing on left click
        if (not self.charging
                and pygame.mouse.get_pressed()[0]):
            
            self.swing(target_group)

        # attacks in a powerful thrust on right click
        # if pygame.mouse.get_pressed()[1] and not self.attacking:
            # self.charge(target_group)

        # clear attack animation if not in combat
        if not self.in_combat:
            self.attacking = False
            self.charging = False

    def swing(self, target_group: pygame.sprite.Group):
        # trigger attack animation
        if pygame.time.get_ticks() - self.attack_time > self.attack_cooldown:
            self.in_combat = True
            if not self.attacking:
                self.frame = 0
                self.attacking = True

            # checks if the player rect overlaps an enemy rect
            colliding_sprites = pygame.sprite.spritecollide(
                self,
                target_group,
                False
            )

            colliding_sprites.sort(key=lambda sprite: math.dist(
                self.hitbox.center,
                sprite.hitbox.center
            ))

            targets_hit = []
            for sprite in colliding_sprites:
                # checks if the player mask overlaps an enemy hitbox
                mask = pygame.mask.from_surface(self.image)
                offset = (sprite.hitbox.x - self.rect.x,
                          sprite.hitbox.y - self.rect.y)

                # when attacking, whole sprite is used as the mask for attack
                # damage is done to hitbox
                if mask.overlap(sprite.rect_mask, offset):
                    # only attacks the penultimate frame
                    if (self.frame == len(self.animation_frames[self.facing]['attack']) - 1
                            and sprite not in targets_hit):

                        sprite.hurt(self.stats)
                        targets_hit.append(sprite)

            # reset attack time if targets hit
            if targets_hit:
                self.attack_time = pygame.time.get_ticks()

    def charge(self, target_group: pygame.sprite.Group):
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

    def hurt(self, stats):
        text_coords = (
            random.randint(
                round((self.hitbox.left + self.hitbox.centerx) / 2),
                round((self.hitbox.right + self.hitbox.centerx) / 2)
            ),
            self.hitbox.top
        )

        dodge = self.stats.dodge_chance >= random.randint(0, 100) / 100
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

                text.set_text(COMICORO[35].render(str(damage), True, ORANGE))
                text.velocity.y = -5

            # non-crit damage
            else:
                text = TextPopUp(
                    text_coords,
                    self.game,
                    self.game.camera_group
                )

                text.set_text(COMICORO[25].render(
                    str(damage),
                    True,
                    TANGERINE
                ))

                text.velocity.y = -5

            self.stats.health -= damage

        # damage is dodged
        else:
            text = TextPopUp(text_coords, self.game, self.game.camera_group)
            text.set_text(COMICORO[20].render('Dodged', True, GOLD))
            text.velocity.y = -5

    def check_death(self):
        if self.stats.health < 0:
            # sprite dies
            self.stats.health = 0
            # self.animation_time = pygame.time.get_ticks()
            # self.cooldown = self.game.player.animation_cooldown

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.enemy_group)
        self.check_state()
        self.check_death()
        self.animation()
