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
        displayInfo = pygame.display.Info()
        self.resolution = displayInfo.current_w, displayInfo.current_h

        self.screen = pygame.display.set_mode(
            self.resolution,
            pygame.DOUBLEBUF,# | pygame.FULLSCREEN
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

        # player
        self.player = Player(
            (0, 0),
            (TILE_SIZE * 1.35,) * 2,
            self,
            (self.camera_group, self.player_group)
        )

        # menu
        self.menu = Menu(self)

        # ui
        self.cursor = Cursor((HALF_TILE_SIZE,) * 2, self, self.cursor_group)
        self.player_health_bar = PlayerHealthBar(
            (TILE_SIZE * 2 + 5, HALF_TILE_SIZE / 2 + 5),
            (TILE_SIZE * 4, HALF_TILE_SIZE),
            self
        )

        self.player_warmth_bar = PlayerWarmthBar(
            (TILE_SIZE + 5, HALF_TILE_SIZE * 1.5 + 10),
            (TILE_SIZE * 2, HALF_TILE_SIZE),
            self
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

        # fills a surface with green
        self.screen.fill(Color.GRASS_GREEN)

        self.camera_group.render(
            show_hitboxes=True,
            show_collision_boxes=True,
            show_rects=False
        )

        self.level.render()

        self.player_health_bar.render()
        self.player_warmth_bar.render()
        self.player.inventory.render()
        self.player.spells.render()

        self.menu.render()
        self.cursor_group.draw(self.screen)

    def update(self):
        '''Updates all sprites and ui'''
        if self.state['unpaused'] and not self.level.transitioning:
            self.camera_group.update()

        self.level.update()

        self.player_health_bar.update()
        self.player_warmth_bar.update()
        self.player.inventory.update()
        self.player.spells.update()

        self.menu.update()
        self.cursor_group.update()


if __name__ == "__main__":
    App().run()
