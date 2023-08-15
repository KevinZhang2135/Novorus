from color import Color
from ui import *
from particles import *
from projectiles import *

import pygame


class Player(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.name = 'Player'
        self.facing = 'right'
        self.actions = ['idle', 'run', 'attack', 'dash']

        # hitbox
        self.set_hitbox(0.15, 0.45, offsety=0.05)
        self.set_collision_box(0.15, 0.15, offsety=0.20)

        # movement and range
        self.max_velocity = 5
        self.dash_velocity = self.max_velocity * 5

        self.melee_range = max(self.hitbox.size) * 1.25

        # stats
        self.exp = 0
        self.stats = Stats(200, 50, 25, 0.05, 0.01)
        self.stats.warmth = 100

        # general animation
        self.animation_frames = {
            'left': {},
            'right': {}
        }

        self.set_animation('player', isFolder=True)

        # animation cooldown
        self.animation_cooldowns = {action: 0 for action in self.actions}
        self.set_animation_cooldown(1000, 800, 800, 600)

        # attack cooldown
        self.targets_hit = []
        self.attack_cooldown = self.animation_cooldowns['attack']
        self.impact_frame = 5

        # dash
        self.dashing = False
        self.dash_time = pygame.time.get_ticks()
        self.dash_cooldown = 1000
        self.dash_duration = 600 # how long a dash lasts

        # inventory
        self.inventory = Inventory(ITEM_TOOLTIPS, self.game)

    def movement(self):
        '''Handles movement'''
        self.acceleration = pygame.math.Vector2()
        if not self.in_combat:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            # creates movement using falsy and truthy values that evaluate to 0 and 1
            self.acceleration.xy = right - left, down - up

        if self.acceleration.length() > 0 and not self.in_combat:  # checks if the player is moving
            # converts the coordinates to a vector according to the radius
            self.acceleration.scale_to_length(self.max_velocity)
            self.velocity += self.acceleration
            self.velocity *= 0.5

        else:
            # movement decay when input is not received
            if self.dashing:
                self.velocity *= 0.925

            else:
                self.velocity *= 0.85

            self.acceleration.xy = 0, 0

        # movement decay when the speed is low
        super().movement()

    def attack_enemy(self, target_group: pygame.sprite.Group):
        self.in_combat = False

        # attacks in a circular swing on left click
        if not self.dashing and pygame.mouse.get_pressed()[0]:
            self.swing(target_group)

        # attacks in a powerful thrust on right click
        elif (not self.attacking
              and not self.dashing
              and pygame.mouse.get_pressed()[2]):

            self.dash()

        if self.dashing:
            self.ram_enemies(target_group)

        # clear attack animation if not in combat
        if not self.in_combat:
            self.attacking = False

    def swing(self, target_group: pygame.sprite.Group):
        # prevents player from moving
        self.in_combat = True

        if pygame.time.get_ticks() - self.attack_time > self.attack_cooldown:
            # trigger attack animation
            if not self.attacking:
                self.frame = 0
                self.attacking = True

            # checks if target is within melee range
            colliding_sprites = [
                sprite for sprite in target_group.sprites()
                if math.dist(self.hitbox.center, sprite.hitbox.center) <= self.melee_range
            ]

            for sprite in colliding_sprites:
                # only attacks during the impact frame
                if (self.frame == self.impact_frame
                        and sprite not in self.targets_hit):

                    # deals damage
                    sprite.hurt(self.stats)
                    self.targets_hit.append(sprite)

                    # randomizes particle position
                    offset = tuple(
                        map(lambda x: x // 4, sprite.hitbox.size)
                    )

                    offset_pos = list(sprite.hitbox.center)
                    for i in range(len(offset_pos)):
                        offset_pos[i] += random.randint(
                            -offset[i],
                            offset[i]
                        )

                    # creates slash particle
                    SwordSlash(
                        offset_pos,
                        (self.hitbox.width * 3,) * 2,
                        self.game,
                        self.game.camera_group
                    )

            # reset attack time if targets hit
            if self.targets_hit:
                self.attack_time = pygame.time.get_ticks()
                self.targets_hit.clear()

    def dash(self):
        '''Dashes a long distance'''

        # prevents player from moving
        self.in_combat = True

        if pygame.time.get_ticks() - self.dash_time > self.dash_cooldown:
            # trigger dash animation
            self.frame = 0
            self.dashing = True

            # dashes where the cursor is pointed
            cursor_pos = self.game.cursor.offset_mouse_pos()
            self.acceleration = pygame.math.Vector2(
                cursor_pos[0] - self.hitbox.center[0],
                cursor_pos[1] - self.hitbox.center[1]
            )

            # dash movement
            if self.acceleration.length() > 0:
                self.acceleration.scale_to_length(self.dash_velocity)
                self.velocity = self.acceleration

                # resets dash time for dash duration
                self.dash_time = pygame.time.get_ticks()

                # creates dust trail
                dust_pos = self.hitbox.midbottom
                dust_trail = DustTrail(
                    dust_pos,
                    (self.hitbox.width * 5,) * 2,
                    self.game,
                    self.game.camera_group
                )

                dust_trail.facing = 'left' if self.velocity.x < 0 else 'right'

    def ram_enemies(self, target_group):
        '''Deals damage to any enemies in collision'''
        self.in_combat = True

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

        for sprite in colliding_sprites:
            # checks if the player mask overlaps an enemy hitbox
            mask = pygame.mask.from_surface(self.image)
            offset = (
                sprite.hitbox.x - self.rect.x,
                sprite.hitbox.y - self.rect.y
            )

            # when dashing, whole sprite is used as the mask for attack
            # damage is done to hitbox
            if mask.overlap(sprite.rect_mask, offset):
                # only attacks the penultimate frame
                if sprite not in self.targets_hit:
                    # deals damage
                    sprite.hurt(self.stats)
                    self.targets_hit.append(sprite)

                    # # randomizes particle position
                    offset = tuple(
                        map(lambda x: x // 4, sprite.hitbox.size)
                    )

                    offset_pos = list(sprite.hitbox.center)
                    for i in range(len(offset_pos)):
                        offset_pos[i] += random.randint(
                            -offset[i],
                            offset[i]
                        )

                    # creates small explosion particle
                    SmallExplosion(
                        offset_pos,
                        (self.hitbox.width * 3,) * 2,
                        self.game,
                        self.game.camera_group
                    )

        # stop dash after duration
        if pygame.time.get_ticks() - self.dash_time > self.dash_duration:
            self.dash_time = pygame.time.get_ticks()
            self.dashing = False

            self.targets_hit.clear()

    def check_state(self):
        '''Determines what action the player is doing'''
        if self.velocity.x < 0:
            self.facing = 'left'

        elif self.velocity.x > 0:
            self.facing = 'right'

        if not self.in_combat:
            if self.velocity.length_squared() > 0:
                self.action = 'run'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            elif self.dashing:
                self.action = 'dash'

            else:
                self.action = 'idle'

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

                text.set_text(str(damage), 25, Color.ORANGE)
                
                text.velocity.y = -5

            # non-crit damage
            else:
                text = TextPopUp(
                    text_coords,
                    self.game,
                    self.game.camera_group
                )

                text.set_text(
                    str(damage),
                    25,
                    Color.TANGERINE
                )

                text.velocity.y = -5

            self.stats.health -= damage

        # damage is dodged
        else:
            text = TextPopUp(text_coords, self.game, self.game.camera_group)
            text.set_text('Dodged', 20, Color.GOLD)
            text.velocity.y = -5

    def check_death(self):
        if self.stats.health < 0:
            # sprite dies
            self.stats.health = 0

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.enemy_group)
        self.check_state()
        self.check_death()
        self.animation()
