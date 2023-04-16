from constants import *
from level import *
from camera_group import *
from ui import *
from entities import Player

import pygame

class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Novorus') 

        # sets the size of the screen; defaults to full screen
        self.resolution = self.width, self.height = 1920, 1080
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF | pygame.FULLSCREEN, 16)
        self.clock = pygame.time.Clock()

        self.state = {
            'unpaused': True,
            'runtime': True,
            'fullscreen': True
        }

    def run(self):
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEMOTION])

        # sprite groups
        self.camera_group = CameraGroup(self)
        self.collision_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()
        self.cursor_group = pygame.sprite.GroupSingle()
        self.light_group = LightSources(self.resolution)

        self.menu = Menu(self)

        self.player_bars = Bars((2, 2), self)
        self.enemy_bars = Bars((2, self.player_bars.height + 4), self)

        # hud
        self.cursor = Cursor(TILE_SIZE, self, self.cursor_group)

        # player
        self.player = Player((0, 0), 
                             (75, 75), 
                             self,
                             (self.camera_group, self.player_group, self.light_group))

        # levels and map
        self.level = Level(STARTING_FLOOR, TILE_SIZE, self)

        while self.state['runtime']:
            # event handling
            for event in pygame.event.get():
                # checks for quit event
                if event.type == pygame.QUIT:
                    self.state['runtime'] = False

            self.screen.fill((105, 162, 97))  # fills a surface with the rgb color

            # redraws sprites and images
            self.camera_group.custom_draw(self.player, show_hitboxes=False)
            self.cursor_group.draw(self.screen)
            self.light_group.render_lighting(self.player)

            self.player_bars.draw(self.player_group)
            self.enemy_bars.draw(self.enemy_group)

            self.menu.draw()
            self.player.inventory.draw()
            self.level.draw()

            # updates
            if self.state['unpaused'] and not self.level.transitioning:
                self.camera_group.update()

            self.cursor_group.update()
            self.menu.update()
            self.player.inventory.update()
            self.level.update()

            # updates screen
            pygame.display.update()
            self.clock.tick(60)

        # closes pygame application
        pygame.font.quit()
        pygame.quit()


if __name__ == "__main__":
    App().run()
