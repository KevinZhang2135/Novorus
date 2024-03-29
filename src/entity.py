from constants import *
from particles import *
from sprite import Sprite

import pygame
from copy import deepcopy


class Stats:
    def __init__(self, health: int, speed: int, attack: int, crit_chance: float, dodge_chance: float, mana=0):
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

        self.mana = mana
        self.base_mana = 100


class Entity(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = ''
        self.facing = 'right'
        self.action = 'idle'

        self.in_combat = False
        self.show_stats = True

        # stats
        self.stats = None

        # movement
        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.max_velocity = 0

        # render
        self.sprite_layer = 3

        # animation
        self.animation_frames = {
            'left': {},
            'right': {}
        }

        # animation cooldowns
        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldowns = {'idle': 0}
        self.animation_cooldown = self.animation_cooldowns[self.action]

        # attack times
        self.attacking = False
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = 0
        self.impact_frame = 0

        # shadows
        self.draw_shadow = True
        self.shadow_frames = deepcopy(self.animation_frames)

    def set_animation(self, filepath: str, isFolder=False):
        '''Sets the animation and corresponding shadows'''
        for facing in self.animation_frames:
            for action in self.animation_cooldowns:
                path = f'{SPRITE_PATH}/{filepath}/{action}'

                if os.path.exists(path):
                    # gets (image, shadow)
                    images = self.get_images(
                        path,
                        isFolder=isFolder,
                        flipped=(facing == 'left')
                    )

                    self.animation_frames[facing][action] = images[0]
                    if self.draw_shadow:
                        self.shadow_frames[facing][action] = images[1]

        # sets image
        self.image = self.animation_frames[self.facing][self.action][self.frame]
        if self.draw_shadow:
            self.shadow = self.shadow_frames[self.facing][self.action][self.frame]

        self.animation_cooldown = self.animation_cooldowns[self.action]

    def line_of_sight(self, point):
        '''Determines whether the line of sight is not obstructed by walls'''
        distance = math.dist(self.hitbox.center, point)

        # filters walls beyond distance to point
        walls = tuple(
            wall for wall in self.game.collision_group.sprites()
            if math.dist(self.hitbox.center, wall.hitbox.center) < distance
        )

        # if any walls obstructing the point
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
        self.map_collision()

        # does not check collision unless speed is greater than 0
        if not self.velocity.magnitude():
            return

        # sorts sprites by distance
        sprites = pygame.sprite.spritecollide(
            self,
            self.game.collision_group,
            False
        )

        sprites.sort(key=lambda sprite: math.dist(
            self.collision_box.center,
            sprite.collision_box.center
        ))

        for sprite in sprites:
            if side := self.detect_collision(sprite):
                match side:
                    # left collision
                    case 'left':
                        self.set_coords(
                            sprite.collision_box.right + self.collision_box.width /
                            2 - self.collision_box_offset.x,
                            self.coords.y
                        )

                    # right collision
                    case 'right':
                        self.set_coords(
                            sprite.collision_box.left - self.collision_box.width /
                            2 - self.collision_box_offset.x,
                            self.coords.y
                        )

                    # top collision
                    case 'top':
                        self.set_coords(
                            self.coords.x,
                            sprite.collision_box.bottom + self.collision_box.height /
                            2 - self.collision_box_offset.y
                        )

                    # bottom collision
                    case 'bottom':
                        self.set_coords(
                            self.coords.x,
                            sprite.collision_box.top - self.collision_box.height /
                            2 - self.collision_box_offset.y
                        )

    def map_collision(self):
        '''Handles map border collision'''
        screen_left = -HALF_TILE_SIZE
        screen_right = self.game.level.rect.right - HALF_TILE_SIZE
        screen_top = -HALF_TILE_SIZE
        screen_bottom = self.game.level.rect.bottom - HALF_TILE_SIZE

        # left edge map
        if self.collision_box.left < screen_left:
            self.velocity.x = 0
            self.set_coords(
                self.collision_box.width / 2 + screen_left - self.collision_box_offset.x + 1,
                self.coords.y
            )

        # right edge map
        elif self.collision_box.right > screen_right:
            self.velocity.x = 0
            self.set_coords(
                screen_right - self.collision_box.width / 2 - self.collision_box_offset.x - 1,
                self.coords.y
            )

        # top edge map
        if self.collision_box.top < screen_top:
            self.velocity.y = 0
            self.set_coords(
                self.coords.x,
                screen_top + self.collision_box.height / 2 - self.collision_box_offset.y + 1
            )

        # bottom edge map
        elif self.collision_box.bottom > screen_bottom:
            self.velocity.y = 0
            self.set_coords(
                self.coords.x,
                screen_bottom - self.collision_box.height / 2 - self.collision_box_offset.y - 1
            )

    def detect_collision(self, sprite):
        '''Determines side of sprite collision using a vector and AABB collision'''

        '''Vector collision'''
        # distance between the centers of two sprites
        center_dist = pygame.math.Vector2(
            self.collision_box.centerx - sprite.collision_box.centerx,
            self.collision_box.centery - sprite.collision_box.centery
        )

        center_dist -= self.velocity * 2

        # creates a line from the player to the point cropped within 
        # collision sprite as a pair of tuples
        velocity_clipline = sprite.collision_box.clipline(
            self.collision_box.center,
            self.collision_box.center - self.velocity
        )

        # track from previous position before displacement if player
        # travels through collision sprite
        if velocity_clipline:
            # horizontal collision
            if abs(center_dist.x) > abs(center_dist.y):
                # left collision
                if center_dist.x > 0:
                    return f'left'

                # right collision
                elif center_dist.x < 0:
                    return f'right'

            elif abs(center_dist.y) > abs(center_dist.x):
                # top collision
                if center_dist.y > 0:
                    return f'top'

                # bottom collision
                elif center_dist.y < 0:
                    return f'bottom'

        '''AABB collision'''
        # does not calculate further or the boxes are not colliding
        # or the distance between centers is greater than collision distance
        if not self.collision_box.colliderect(sprite.collision_box):
            return

        # the distance of the sprite intersection area
        intersect_dist = pygame.math.Vector2(
            *map(lambda x: abs(x), self.velocity)
        )

        # intersection zones
        # left side intersect
        if center_dist.x > 0:
            intersect_dist.x = sprite.collision_box.right - self.collision_box.left

        # right side intersect
        elif center_dist.x < 0:
            intersect_dist.x = self.collision_box.right - sprite.collision_box.left

        # top side intersect
        if center_dist.y < 0:
            intersect_dist.y = self.collision_box.bottom - sprite.collision_box.top

        # bottom side intersect
        elif center_dist.y > 0:
            intersect_dist.y = sprite.collision_box.bottom - self.collision_box.top

        # horizontal collision
        # the side intersecting the least is the side colliding
        if intersect_dist.x < intersect_dist.y:
            # left collision
            if center_dist.x > 0:
                return f'left'

            # right collision
            elif center_dist.x < 0:
                return f'right'

        # vertical collision
        elif intersect_dist.y < intersect_dist.x:
            # top collision
            if center_dist.y > 0:
                return f'top'

            # bottom collision
            elif center_dist.y < 0:
                return f'bottom'

    def face_enemy(self, target: Sprite):
        if self.hitbox.centerx < target.hitbox.centerx:
            self.facing = 'right'

        else:
            self.facing = 'left'

    def attack_enemy(self, target_group):
        pass

    def check_state(self):
        if not self.attacking:
            # if entity is moving
            if self.velocity.length_squared() > 0:
                self.action = 'run'
                self.facing = 'left' if self.velocity.x < 0 else 'right'

            else:
                self.action = 'idle'

        else:
            self.action = 'attack'

        if not self.animation_frames[self.facing][self.action]:
            self.action = 'idle'

    def hurt(self, stats):
        '''Deals damage to sprite according to stats'''

        # randomizes particle position
        text_coords = (
            random.randint(
                (self.hitbox.left + self.hitbox.centerx) // 2,
                (self.hitbox.right + self.hitbox.centerx) // 2
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

                text.set_text(str(damage), 35, Color.BLOOD_RED)
                text.velocity.y = -5

            # non-crit damage
            else:
                text = TextPopUp(
                    text_coords,
                    self.game,
                    self.game.camera_group
                )

                text.set_text(str(damage), 25, Color.RED)
                text.velocity.y = -5

            # takes damage
            self.stats.health -= damage

        # damage is dodged
        else:
            text = TextPopUp(text_coords, self.game, self.game.camera_group)
            text.set_text('Dodged', 20, Color.GOLD)
            text.velocity.y = -5

    def check_death(self):
        # does not kill sprite unless health is below 0
        if not self.stats.health <= 0:
            return

        # sprite dies
        self.stats.health = 0

        # creates dust cloud on death
        x_offset = round((self.hitbox.right - self.hitbox.left) / 4)
        x = random.randint(
            self.hitbox.centerx - x_offset,
            self.hitbox.centerx + x_offset
        )

        y_offset = round((self.hitbox.bottom - self.hitbox.top) / 4)
        y = random.randint(
            self.hitbox.centery - y_offset,
            self.hitbox.centery + y_offset
        )

        dust_width = randomize(min(*self.hitbox.size), 0.05) * 3

        Explosion3(
            (x, y),
            (dust_width,) * 2,
            self.game,
            self.game.camera_group
        )

        self.kill()
        del self

    def animation(self):
        '''Handles animation'''
        self.animation_cooldown = self.animation_cooldowns[self.action]

        # loops frames
        if self.loop_frames and self.frame >= len(self.animation_frames[self.facing][self.action]):
            self.frame = 0

        # set image
        if self.frame < len(self.animation_frames[self.facing][self.action]):
            self.image = self.animation_frames[self.facing][self.action][self.frame]
            if self.draw_shadow:
                self.shadow = self.shadow_frames[self.facing][self.action][self.frame]

            # determines whether the animation cooldown is over
            if (self.animation_cooldown
                    and pygame.time.get_ticks() - self.animation_time > self.animation_cooldown):

                self.animation_time = pygame.time.get_ticks()
                self.frame += 1

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.player_group)
        self.check_state()
        self.check_death()
        self.animation()


class MeleeEntity(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        # movement and range
        self.detection_distance = 0
        self.max_velocity = 0
        self.melee_range = 0

        self.targets_hit = []

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

    def attack_enemy(self, target_group):
        # checks if target is within melee range
        self.in_combat = False
        colliding_sprites = [
            sprite for sprite in target_group.sprites()
            if math.dist(self.hitbox.center, sprite.hitbox.center) <= self.melee_range
        ]

        for sprite in colliding_sprites:
            self.in_combat = True
            self.face_enemy(sprite)

            if pygame.time.get_ticks() - self.attack_time > self.attack_cooldown:
                # trigger attack animation
                if not self.attacking:
                    self.frame = 0
                    self.attacking = True

                # only attacks during the impact frame
                if (self.frame == self.impact_frame
                        and sprite not in self.targets_hit):

                    sprite.hurt(self.stats)
                    self.targets_hit.append(sprite)

        if self.targets_hit:
            self.attack_time = pygame.time.get_ticks()
            self.targets_hit.clear()

        # clear attack animation if not in combat
        if not self.in_combat:
            self.attacking = False


class RangerEntity(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.has_fired_projectile = False

        # movement and range
        self.detection_distance = 0
        self.max_velocity = 0
        self.attack_range = 0

    def movement(self):
        '''Handles movement'''
        self.acceleration = pygame.math.Vector2(
            self.game.player.rect.centerx - self.rect.centerx,
            self.game.player.rect.centery - self.rect.centery
        )

        player_distance = math.dist(
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

    def attack_enemy(self, target_group):
        # Attacks closest target with a projectile

        # checks if the target rect is within attack range
        targets = target_group.sprites()
        targets.sort(key=lambda sprite: math.dist(
            self.hitbox.center,
            sprite.hitbox.center
        ))

        # attacks when target is within attack range
        if (len(targets) > 0
                and math.dist(self.hitbox.center, targets[0].hitbox.center) < self.attack_range
                and self.line_of_sight(targets[0].hitbox.center)):

            self.in_combat = True
            self.face_enemy(targets[0])  # closest enemy

            # only attacks the last frame
            if (pygame.time.get_ticks() - self.attack_time > self.attack_cooldown):
                # trigger attack animation
                if not self.attacking:
                    self.frame = 0
                    self.attacking = True
                    self.has_fired_projectile = False

                # shoot projectile after animation ends
                if self.frame == self.impact_frame and not self.has_fired_projectile:
                    self.create_projectile(targets[0])
                    self.has_fired_projectile = True

                # stops attack animation
                if self.frame == len(self.animation_frames[self.facing]['attack']) - 1:
                    self.attack_time = pygame.time.get_ticks()
                    self.attacking = False

        # cancels attack when target moves outside attack range
        else:
            self.attacking = False
            self.in_combat = False

    def create_projectile(self, target):
        pass
