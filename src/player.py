from effects import *
from entity import *
from projectiles import *
from ui import *


import pygame


class Player(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)

        self.show_stats = True
        self.action = 'idle'
        self.facing = 'right'
        self.name = 'Player'

        # hitbox
        self.set_hitbox(0.15, 0.3)

        # movement
        self.max_velocity = 6

        # stats
        self.exp = 0  # max exp is 9900
        self.exp_levels = [i for i in range(100, 10000, 100)]
        self.level = 1
        while self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

        self.stats = Stats(100, 50, 20, 0.05, 0.01)

        # general animation
        self.frame = 0
        self.animation_types = {
            'idle': [],
            'run': [],
            'attack': []
        }

        for type in self.animation_types:
            num_of_frames = len(os.listdir(f'{SPRITE_PATH}/player/{type}'))
            for i in range(num_of_frames):
                image = IMAGES[f'knight_{type}{i + 1}'].copy()
                image = pygame.transform.scale(
                    image,
                    size
                )

                self.animation_types[type].append(image)

        self.image = self.animation_types['idle'][self.frame]

        self.animation_time = pygame.time.get_ticks()
        self.animation_cooldown = 1500 / len(self.animation_types['idle'])

        # attack speed and animation
        self.attack_time = pygame.time.get_ticks()
        self.attack_cooldown = (700 - self.stats.speed) \
            / len(self.animation_types['attack'])

        if self.attack_cooldown < 50:
            self.attack_cooldown = 50

        self.cooldown = self.animation_cooldown

        # inventory
        self.inventory = Inventory(ITEM_TOOLTIPS, self.game)
        self.inventory.add_item('wood_sword', 1)

        # lighting
        self.light_size = pygame.math.Vector2(900, 900)

        self.light = IMAGES['soft_circle'].copy()
        self.light = pygame.transform.scale(
            self.light,
            [int(dimension) for dimension in self.light_size]
        )

        self.light = color_image(self.light, LIGHT_GREY, transparency=255)

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
        if abs(self.velocity.x) < self.max_velocity / 100:
            self.velocity.x = 0

        if abs(self.velocity.y) < self.max_velocity / 100:
            self.velocity.y = 0

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

    def leveling_up(self):
        '''Increases player level when they reach exp cap'''
        if self.exp > self.exp_levels[self.level - 1]:
            self.level += 1

    def attack_enemy(self, target_group: pygame.sprite.Group):
        self.attacking = False
        self.cooldown = self.animation_cooldown

        # attacks on click
        if pygame.mouse.get_pressed()[0]:
            self.attacking = True
            self.cooldown = self.attack_cooldown
            
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
            #print(self.frame, len(self.animation_types['attack']))
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
                            and self.frame == len(self.animation_types['attack']) - 1):
                        self.attack_time = pygame.time.get_ticks()
                        sprite.hurt(self.stats.attack, self.stats.crit_chance)


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

    def hurt(self, attack, crit_chance):
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

                text.set_text(COMICORO[35].render(str(damage), True, ORANGE))
                text.velocity.y = -5

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

        else:
            text = TextPopUp(text_coords, self.game, self.game.camera_group)
            text.set_text(COMICORO[20].render('Dodged', True, GOLD))
            text.velocity.y = -5

    def check_death(self):
        if self.stats.health < 0:
            # sprite dies
            self.stats.health = 0
            self.animation_time = pygame.time.get_ticks()
            self.cooldown = self.game.player.animation_cooldown

    def update(self):
        '''Handles events'''
        self.movement()
        self.collision()
        self.attack_enemy(self.game.enemy_group)
        self.check_state()
        self.check_death()
        self.animation()
        self.leveling_up()
