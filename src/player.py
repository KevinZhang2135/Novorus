from constants import *
from ui import *
from inventory import Inventory
from spells import *
from particles import *
from projectiles import *
from inventory import Item

import pygame


class Player(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Player'
        self.facing = 'right'

        # hitbox
        self.set_hitbox(0.15, 0.45, offsety=0.05)
        self.set_collision_box(0.15, 0.15, offsety=0.2)

        # movement and range
        self.max_velocity = 5
        self.dash_velocity = self.max_velocity * 5

        self.melee_range = max(self.hitbox.size) * 1.25

        # stats
        self.stats = Stats(200, 50, 25, 0.05, 0.01)
        self.stats.mana = 100

        # general animation
        self.animation_cooldowns = {
            'idle': 100,
            'run': 100,
            'attack': 75,
            'dash': 75,
            'cast_action': 100,
            'cast_anticip': 100,
            'cast_recover': 100
        }

        self.animation_frames = {
            'left': {},
            'right': {}
        }

        self.set_animation('player', isFolder=True)

        # attack cooldown
        self.targets_hit = []
        self.attack_cooldown = self.animation_cooldowns['attack']
        self.impact_frame = 5

        # dash
        self.dashing = False
        self.dash_time = pygame.time.get_ticks()
        self.dash_cooldown = 1000
        self.dash_duration = 600  # how long a dash lasts

        # cast
        self.casting = True
        self.casting_phase = -1
        self.casting_phases = ('cast_anticip', 'cast_action', 'cast_recover')
        self.cast_time = pygame.time.get_ticks()

        # inventory
        inventory_rect_width = TILE_SIZE * 4
        inventory_coords = (
            5, 
            (self.game.height - inventory_rect_width) - 5
        )

        self.inventory = Inventory(
            inventory_coords,
            ITEM_TOOLTIPS,
            self.game
        )

        for i in range(35):
            name = f'Item{i}'
            self.inventory.items[name] = Item(
                name, 
                IMAGES['baguette'], 
                (f'tooltip{i}',), 
                0, 
                self.game
            )
            
            self.inventory.add(self.inventory.items[name])

        # spells
        self.spells = SpellGroup(self.game)

    def movement(self):
        '''Handles movement'''
        if not self.in_combat:
            keys = self.game.keys_pressed
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            up = keys[pygame.K_UP] or keys[pygame.K_w]

            # creates movement using falsy and truthy values that evaluate to 0 and 1
            self.acceleration.xy = right - left, down - up

        # checks if the player is moving
        if self.acceleration.length() > 0 and not self.in_combat:
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

        # movement decay when the speed is low
        super().movement()

    def attack_enemy(self, target_group):
        if not self.attacking and not self.dashing:
            # attacks in a circular swing on left click
            if pygame.mouse.get_pressed()[0]:
                self.slash()

            # attacks in a powerful thrust on right click
            elif pygame.mouse.get_pressed()[2]:
                self.dash()

            else:
                # casts a devastating spell on space key
                if self.game.keys_pressed[pygame.K_SPACE]:
                    self.cast(target_group)

                else:
                    self.casting = False
                    self.casting_phase = -1

        self.damage_enemies(target_group)

    def slash(self):
        '''Triggers slash attack'''

        # prevents player from moving
        self.in_combat = True

        if pygame.time.get_ticks() - self.attack_time > self.attack_cooldown:
            # trigger attack animation
            self.frame = 0
            self.attacking = True

    def dash(self):
        '''Dashes a long distance'''
        # prevents player from moving
        self.in_combat = True

        # does not dash unless time elapsed exceeds cooldown
        if not pygame.time.get_ticks() - self.dash_time > self.dash_cooldown:
            return

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

    def cast(self, target_group):
        '''Casts a devastating spell to obliterate enemies'''
        spell = self.spells.sprites()[0]
        casting_phase = self.casting_phases[self.casting_phase]

        # prevents player from moving
        self.in_combat = True
        if spell != self.spells.empty_spell:
            # triggers cast animation
            self.casting = True

            match (self.casting_phase):
                case -1:
                    self.frame = 0
                    self.casting_phase += 1

                case 0 | 2:
                    # triggers next casting phase

                    # casting phases 0 and 2 are dependent on frames
                    if self.frame == len(self.animation_frames[self.facing][casting_phase]):
                        self.frame = 0
                        self.casting_phase += 1
                        self.cast_time = pygame.time.get_ticks()

                        if self.casting_phase >= len(self.casting_phases):
                            self.casting_phase = 0

                case 1:
                    # casting phase 1 continuously loops until duration is met
                    if pygame.time.get_ticks() - self.cast_time > spell.cast_duration:
                        self.frame = 0
                        self.casting_phase += 1

                        cursor_pos = self.game.cursor.offset_mouse_pos()
                        spell.cast(cursor_pos, self.stats, target_group)

                        # uses mana
                        self.stats.mana -= spell.cost
                        if self.stats.mana < 0:
                            # exceeding limit spends life
                            mana_ratio = self.stats.mana / self.stats.base_mana
                            damage = round(self.stats.base_health * mana_ratio)

                            self.stats.health += damage
                            self.stats.mana = 0

                        # after max uses, destroy weapon
                        if spell.uses <= 0:
                            spell.kill()
                            del spell

        else:
            # ends casting animation after weapon is destroyed
            if (self.casting_phase == 2
                    and self.frame == len(self.animation_frames[self.facing][casting_phase])):
                self.frame = 0

                self.casting = False
                self.casting_phase = -1

    def damage_enemies(self, target_group):
        """Deals damage to targets"""

        # deals damage to all targets within attack range
        if self.attacking:
            self.deal_melee_damage(target_group)

        # deals damage to all targets within dash
        elif self.dashing:
            self.deal_dash_damage(target_group)

        # unlocks player movement if not attacking
        elif not self.casting:
            self.in_combat = False

    def deal_melee_damage(self, target_group):
        '''Deals damage to all targets within attack range'''

        # only attacks during the impact frame
        if self.frame == self.impact_frame:
            # checks if target is within melee range
            colliding_sprites = [
                sprite for sprite in target_group.sprites()
                if math.dist(self.hitbox.center, sprite.hitbox.center) <= self.melee_range
            ]

            for sprite in colliding_sprites:
                if sprite not in self.targets_hit:

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

        # clears pierce and cooldown after animation ends
        if self.frame == len(self.animation_frames[self.facing]['attack']):
            self.attack_time = pygame.time.get_ticks()
            self.targets_hit.clear()

            self.in_combat = False
            self.attacking = False

    def deal_dash_damage(self, target_group):
        '''Deals damage to any enemies in collision'''

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
                    Explosion2(
                        offset_pos,
                        (self.hitbox.width * 3,) * 2,
                        self.game,
                        self.game.camera_group
                    )

        # stop dash after duration
        if pygame.time.get_ticks() - self.dash_time > self.dash_duration:
            self.dash_time = pygame.time.get_ticks()
            self.targets_hit.clear()

            self.in_combat = False
            self.dashing = False

    def check_state(self):
        '''Determines what action the player is doing'''
        if self.velocity.x < 0:
            self.facing = 'left'

        elif self.velocity.x > 0:
            self.facing = 'right'

        if not self.in_combat:
            if self.velocity.x or self.velocity.y:
                self.action = 'run'

            else:
                self.action = 'idle'

        else:
            if self.attacking:
                self.action = 'attack'

            elif self.dashing:
                self.action = 'dash'

            elif self.casting:
                # maps casting action to phase
                self.action = self.casting_phases[self.casting_phase]

            else:
                self.action = 'idle'

    def hurt(self, stats):
        '''Deals damage to player according to stats'''

        # randomizes particle position
        text_coords = (
            random.randint(
                (self.hitbox.left + self.hitbox.centerx) // 2,
                (self.hitbox.right + self.hitbox.centerx) // 2
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
