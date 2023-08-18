from constants import *
from sprite import Sprite

import pygame


class Particle(Sprite):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # movement
        self.acceleration = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()

        # render
        self.alpha = 255
        self.sprite_layer = 4
        self.draw_shadow = False
        self.loop_frames = False

        # fade
        self.fade = True
        self.fade_time = pygame.time.get_ticks()
        self.fade_cooldown = 1000

        # hitboxes are not used for collision
        self.set_hitbox(0, 0)

    def movement(self):
        '''Handles movement'''
        self.velocity += self.acceleration
        self.velocity *= 0.9

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

    def expire(self):
        '''Fades particle after its fade time
           Deletes the particle if it has no alpha'''
        if pygame.time.get_ticks() - self.fade_time > self.fade_cooldown:
            self.alpha -= 8
            if self.alpha > 0 and self.fade:
                self.image.set_alpha(self.alpha)

            else:
                self.kill()
                del self

    def update(self):
        '''Handles events'''
        self.movement()
        self.animation()
        self.expire()


class CircleParticle(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        self.color = None

    def set_circles(self):
        # creates an animation of shrinking circles
        animation_frames = []
        for radius in range(width := round(self.size.x / 2), width // 2, -width // 20):
            animation_frames.append(get_circle_surface(radius, self.color))

        # set circle image
        for facing in self.animation_frames:
            self.animation_frames[facing] = animation_frames

        self.image = self.animation_frames[self.facing][self.frame]

    def movement(self):
        '''Handles movement'''
        self.velocity += self.acceleration

        self.set_coords(
            self.coords.x + self.velocity.x,
            self.coords.y + self.velocity.y
        )

    def update(self):
        self.movement()
        self.animation()
        self.expire()


class DustStomp(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # render
        self.animation_cooldown = 100
        self.fade_cooldown = 500

        self.set_animation('particles/dust_stomp', isFolder=True)


class DustTrail(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # render
        self.animation_cooldown = 100
        self.set_animation('particles/dust_trail', isFolder=True)


class Explosion1(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        # fiery, yellow explosion

        # render
        self.fade = False
        self.fade_cooldown = 850
        
        self.animation_cooldown = 100
        self.set_animation('particles/explosion1_', isFolder=True)
        

        # light
        self.draw_light = True
        self.light_color = Color.GOLD
        self.light_radius = 30


class Explosion2(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        # small, circular explosion

        # render
        self.animation_cooldown = 150
        self.fade_cooldown = 150

        self.set_animation('particles/explosion2_', isFolder=True)

class Explosion3(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)
        # circular, grey explosion

        # render
        self.animation_cooldown = 100
        self.fade_cooldown = 600

        self.set_animation('particles/explosion3_', isFolder=True)


class SwordSlash(Particle):
    def __init__(self, coords: list, size: list, game, groups):
        super().__init__(coords, size, game, groups)

        # render
        self.facing = random.choice(('left', 'right'))
        self.animation_cooldown = 100
        self.fade_cooldown = 200

        self.set_animation('particles/sword_slash', isFolder=True)


class TextPopUp(Particle):
    def __init__(self, coords: list, game, group):
        super().__init__(coords, [0, 0], game, group)

    def set_text(self, text, font_size, color):
        self.image = COMICORO[font_size].render(text, True, color)
        self.rect = self.image.get_rect(center=self.coords)
        self.hitbox = pygame.Rect(self.rect)
