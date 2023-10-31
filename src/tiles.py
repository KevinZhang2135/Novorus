from constants import *
from particles import *
from sprite import Sprite
from entity import *

import pygame


class WoodChest(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.action = 'closed'

        # hitbox
        self.set_hitbox(0.55, 0.25, offsety=0.1)
        self.set_collision_box(0.55, 0.25, offsety=0.1)

        # render
        self.sprite_layer = 3

        # animation
        self.animation_cooldowns = {
            'closed': 0,
            'opened': 0
        }

        self.animation_frames = {
            'left': {},
            'right': {}
        }

        self.set_animation('chest', isFolder=True)

        # chest contents
        self.items = {}
        self.spell = None

    def check_state(self):
        # checks if the distance of the sprites are within collision distance
        if self.action == 'closed' and pygame.Rect.colliderect(self.rect, self.game.player.hitbox):
            self.action = 'opened'

            for name, count in self.items.items():
                self.game.player.inventory.add_item(
                    name,
                    count
                )

            if self.spell:
                self.game.player.spells.add(
                    self.spell
                )

    def update(self):
        self.check_state()
        self.animation()


class Torch(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # hitbox
        self.set_hitbox(0.15, 0.3)

        # render
        self.sprite_layer = 4

        # animation
        self.animation_cooldown = 125
        self.set_animation('decor/animated/torch', isFolder=True)

        # smoke
        self.smoke_time = pygame.time.get_ticks()
        self.smoke_cooldown = randomize(500, 0.2)

        # light
        self.draw_light = True
        self.light_radius = 50
        self.light_color = Color.GOLD

    def draw_smoke(self):
        "Creates smoke every interval"
        # does not draw smoke unless time elapsed exceeds cooldown
        if not pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            return
            
        self.smoke_time = pygame.time.get_ticks()
        smoke_pos = list(self.hitbox.midtop)
        smoke_pos[0] += random.randint(
            width := -self.hitbox.width // 4,
            -width
        )

        smoke_pos[1] -= self.hitbox.width // 4

        # creates circle particle for smoke
        smoke = CircleParticle(
            smoke_pos,
            (randomize(self.hitbox.width * 1.1, 0.1),) * 2,
            self.game,
            self.game.camera_group
        )

        # smoke render
        smoke.animation_cooldown = 100
        smoke.fade_cooldown = 500
        smoke.color = random.choice((Color.ASH, Color.BLACK))

        smoke.set_circles()

        # smoke movement
        smoke.velocity.y = -0.25

    def update(self):
        self.animation()
        self.draw_smoke()


class Totem(Entity):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

    def hurt(self, stats):
        # deals damage to sprite

        # randomizes particle position
        offset = tuple(
            map(lambda x: x // 4, self.hitbox.size)
        )

        offset_pos = list(self.hitbox.center)
        for i in range(len(offset_pos)):
            offset_pos[i] += random.randint(
                -offset[i],
                offset[i]
            )

        # randomizes damage between 0.9 and 1.1
        damage = randomize(stats.attack, 0.15)

        # doubles damage if crit
        crit = stats.crit_chance >= random.randint(0, 100) / 100
        if crit:
            damage *= 2

            text = TextPopUp(
                offset_pos,
                self.game,
                self.game.camera_group
            )

            text.set_text(str(damage), 35, Color.BLOOD_RED)

        # non-crit damage
        else:
            text = TextPopUp(
                offset_pos,
                self.game,
                self.game.camera_group
            )

            text.set_text(str(damage), 25, Color.RED)

        text.velocity.y = -5

        # takes damage
        self.stats.health -= damage

        for i in range(random.randint(6, 9)):
            # creates circle particle for sparks
            sparks = CircleParticle(
                self.hitbox.center,
                (randomize(self.hitbox.width * 0.3, 0.5),) * 2,
                self.game,
                self.game.camera_group
            )

            # sparks render
            sparks.animation_cooldown = 50
            sparks.fade_cooldown = randomize(150, 0.5)
            sparks.color = random.choice((
                Color.SKY_BLUE1,
                Color.SKY_BLUE2,
                Color.SKY_BLUE3
            ))

            sparks.set_circles()

            # sparks movement
            sparks.velocity.x = random.uniform(-2, 2)
            sparks.velocity.y = -randomize(2.5, 0.5)
            sparks.acceleration.y = 0.25

    def check_death(self):
        if self.stats.health <= 0:
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

    def make_exit(self):
        '''Creates portal when all totems are destroyed'''
        if not self.game.totem_group.sprites():
            LevelExit(
                self.hitbox.midbottom,
                (TILE_SIZE * 0.5,) * 2,
                self.game,
                self.game.camera_group
            )

    def update(self):
        self.check_state()
        self.check_death()
        self.make_exit()
        self.animation()


class Totem1(Totem):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Mysterious Totem'

        # hitbox
        self.set_hitbox(0.3, 0.875)

        # stats
        self.exp = 25
        self.stats = Stats(200, 0, 0, 0, 0)

        # animation
        self.animation_cooldowns = {'idle': 0}
        self.set_animation('enemies/totem1', isFolder=True)
        


class Totem2(Totem):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.name = 'Mysterious Totem'

        # hitbox
        self.set_hitbox(0.3, 0.4)

        # stats
        self.exp = 25
        self.stats = Stats(150, 0, 0, 0, 0)

        # animation
        self.animation_cooldowns = {'idle': 100}
        self.set_animation('enemies/totem2', isFolder=True)


class LevelExit(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # hitbox
        self.set_hitbox(0.7, 0.5)

        # render
        self.sprite_layer = 3

        # animation
        self.set_animation('exit', isFolder=True)

        # animation cooldown
        self.animation_cooldown = 700 / len(self.animation_frames[self.facing])

    def transition_level(self):
        if pygame.sprite.spritecollide(self, self.game.player_group, False):
            # checks if the player mask overlaps an enemy mask
            mask = pygame.mask.from_surface(self.image)
            offset = (
                self.game.player.hitbox.x - self.rect.x,
                self.game.player.hitbox.y - self.rect.y
            )

            if mask.overlap(self.game.player.rect_mask, offset):
                self.game.level.transitioning = True

    def update(self):
        self.transition_level()
        self.animation()
