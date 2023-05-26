from effects import *
from entities import *
from ui import *

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

        self.stats = Stats(100, 10000, 200, 0.05, 0.01)

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
        
        if self.attack_cooldown < 100:
            self.attack_cooldown = 100

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


