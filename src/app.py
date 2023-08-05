from constants import *
from camera_group import CameraGroup
from level import *
from ui import *
from player import Player

import pygame


class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Novorus')
        pygame.mouse.set_visible(False)

        # sets the size of the screen; defaults to full screen
        self.resolution = 1920, 1080
        self.screen = pygame.display.set_mode(
            self.resolution,
            pygame.DOUBLEBUF | pygame.FULLSCREEN
        )

        # ticks and state
        self.events = []
        self.clock = pygame.time.Clock()
        self.state = {
            'unpaused': True,
            'runtime': True,
            'fullscreen': True
        }

        # sprite groups
        self.camera_group = CameraGroup(self)
        self.collision_group = pygame.sprite.Group()

        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()
        self.totem_group = pygame.sprite.Group()

        self.cursor_group = pygame.sprite.GroupSingle()

        # menu
        self.menu = Menu(self)

        # ui bars
        self.player_bars = BarGroup((2, 2), self)
        self.enemy_bars = BarGroup((2, self.player_bars.height + 4), self)

        # hud
        self.cursor = Cursor((HALF_TILE_SIZE,) * 2, self, self.cursor_group)

        # player
        self.player = Player(
            (0, 0),
            (TILE_SIZE * 1.35,) * 2,
            self,
            (self.camera_group, self.player_group)
        )

        # levels and map
        self.level = Level(STARTING_FLOOR, self)

    def run(self):
        pygame.event.set_allowed((pygame.QUIT, pygame.MOUSEWHEEL))

        while self.state['runtime']:
            # event handling
            self.events = pygame.event.get()

            # checks for quit event
            if pygame.QUIT in self.events:
                self.state['runtime'] = False

            # fills a surface with the rgb color
            self.screen.fill((105, 162, 97))

            self.draw()
            self.update()

            # updates screen
            pygame.display.update()
            self.clock.tick(60)

        # closes pygame application
        pygame.font.quit()
        pygame.quit()

    def draw(self):
        '''Redraws sprites, images, and surfaces'''
        self.camera_group.render(
            show_hitboxes=False,
            show_rects=False
        )

        # ui
        self.player_bars.draw(self.player_group, always_show=True)
        self.enemy_bars.draw(self.enemy_group)

        self.menu.draw()
        self.player.inventory.draw()
        self.level.draw()
        self.cursor_group.draw(self.screen)

    def update(self):
        '''Updates all sprites and ui'''
        if self.state['unpaused'] and not self.level.transitioning:
            self.camera_group.update()

        self.cursor_group.update()
        self.menu.update()
        self.player.inventory.update()
        self.level.update()


if __name__ == "__main__":
    App().run()
