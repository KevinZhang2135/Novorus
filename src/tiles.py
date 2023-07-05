from constants import *
from particles import *
from sprite import Sprite
from entity import *

import pygame


class Chest(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.opened = False

        # hitbox
        self.hitbox = self.rect.scale_by(0.55, 0.45)

        # render
        self.sprite_layer = 3

        # sprites
        self.chest_closed = IMAGES['chest_closed'].copy()
        self.chest_closed = pygame.transform.scale(
            self.chest_closed,
            size
        )

        self.chest_opened = IMAGES['chest_opened'].copy()
        self.chest_opened = pygame.transform.scale(
            self.chest_opened,
            size
        )

        self.image = self.chest_closed

    def collision(self):
        # checks if the distance of the sprites are within collision distance
        if pygame.Rect.colliderect(self.rect, self.game.player.hitbox) and not self.opened:
            self.image = self.chest_opened
            self.opened = True

            self.game.player.inventory.add_item(
                'baguette',
                random.randint(1, 3)
            )

            self.game.player.inventory.add_item(
                'oak_log',
                random.randint(1, 3)
            )

    def update(self):
        self.collision()


class Torch(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # hitbox
        self.set_hitbox(0.15, 0.3)

        # render
        self.sprite_layer = 4

        # animation
        self.set_animation('decor/animated/torch', isFolder=True)
        self.animation_cooldown = 600 / len(self.animation_frames[self.facing])
        self.cooldown = self.animation_cooldown

        # smoke
        self.smoke_time = pygame.time.get_ticks() + random.randint(1000, 2000)
        self.smoke_cooldown = randomize(4000, 0.2)

        self.smoke_frames = len(
            os.listdir(f'{SPRITE_PATH}/particles/smoke')
        )

    def draw_smoke(self):
        "Creates smoke every interval"
        if pygame.time.get_ticks() - self.smoke_time > self.smoke_cooldown:
            self.smoke_time = pygame.time.get_ticks()
            self.smoke_cooldown = randomize(4000, 0.2)

            smoke = Particle(
                self.rect.center,
                [randomize(25, 0.1) for i in range(2)],
                self.game,
                self.game.camera_group
            )

            smoke.set_animation(f'particles/smoke/smoke{random.randint(1, self.smoke_frames)}')
            smoke.velocity.y = -4
            smoke.expiration_time = 500

    def update(self):
        self.animation()
        self.draw_smoke()


class Totem(Entity):
    def __init__(self, coords: list, size: list, game, groups: pygame.sprite.Group):
        super().__init__(coords, size, game, groups)
        self.name = 'Mysterious Totem'

        # hitbox
        self.set_hitbox(0.225, 0.375)

        # stats
        self.exp = 25
        self.stats = Stats(300, 0, 0, 0, 0)

        # animation
        self.set_animation('enemies/totem', isFolder=True)
        self.animation_cooldown = 700 / len(self.animation_frames[self.facing]['idle'])
        self.cooldown = self.animation_cooldown

    def make_exit(self):
        '''Creates portal when all totems are destroyed'''
        if not self.game.totem_group.sprites():
            LevelExit(
                self.hitbox.midbottom, 
                (TILE_SIZE * 0.5, ) * 2,
                self.game,
                self.game.camera_group
            )

    def update(self):
        self.check_state()
        self.check_death()
        self.make_exit()
        self.animation()


class LevelExit(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # hitbox
        self.set_hitbox(0.7, 0.5)

        # render
        self.sprite_layer = 3

        # animation
        self.set_animation('exit', isFolder=True)
        self.animation_cooldown = 700 / len(self.animation_frames[self.facing])
        self.cooldown = self.animation_cooldown


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

                