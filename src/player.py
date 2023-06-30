from lighting import *
from particles import *
from projectiles import *
from ui import *


import pygame
import math


class Player(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.name = 'Player'
        self.facing = 'right'

        # hitbox
        self.set_hitbox(0.15, 0.3)

        # movement
        self.max_velocity = 6

        # stats
        self.exp = 0

        self.stats = Stats(100, 50, 20, 0.05, 0.01)

        # general animation
        self.set_animation('player')
        self.image = self.animation_frames['idle'][self.frame]

        self.animation_cooldown = 1500 / len(self.animation_frames['idle'])

        # attack speed and animation
        self.attack_cooldown = (700 - self.stats.speed) \
            / len(self.animation_frames['attack'])

        if self.attack_cooldown < 50:
            self.attack_cooldown = 50

        self.cooldown = self.animation_cooldown

        # inventory
        self.inventory = Inventory(ITEM_TOOLTIPS, self.game)
        self.inventory.add_item('wood_sword', 1)

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
        # attacks on click
        self.in_combat = False
        if pygame.mouse.get_pressed()[0]:
            # trigger attack animation
            self.in_combat = True
            if not self.attacking:
                self.frame = 0
                self.attacking = True 
                self.cooldown = self.attack_cooldown

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
                    # only attacks the last frame
                    if (pygame.time.get_ticks() - self.attack_time > self.attack_cooldown
                            and self.frame == len(self.animation_frames['attack'])
                            and sprite not in targets_hit):

                        sprite.hurt(self.stats)
                        targets_hit.append(sprite)

            # reset attack time if targets hit
            if targets_hit:
                self.attack_time = pygame.time.get_ticks()

        # clear attack animation if not in combat
        if not self.in_combat:
            self.attacking = False
            self.cooldown = self.animation_cooldown

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
            #self.animation_time = pygame.time.get_ticks()
            #self.cooldown = self.game.player.animation_cooldown

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.enemy_group)
        self.check_state()
        self.check_death()
        self.animation()
