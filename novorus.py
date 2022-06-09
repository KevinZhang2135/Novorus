import pygame
from novorus_func import *

pygame.init()
pygame.display.set_caption('Novorus')

screen = pygame.display.set_mode((1080, 720)) # sets the dimensions of the screen; defaults to full screen
clock = pygame.time.Clock()

sprites = pygame.sprite.Group()

for i in range(0, 300, 200):
    ghost = Ghost((i, 100), 75, 75)    
    sprites.add(ghost)
    
for i in range(0, 500, 100):
    wall = Wall((i, 300), 100, 100)    
    sprites.add(wall)
    
chest = Chest((300, 200), 80, 80)
sprites.add(chest)
    
player = Player((300, 0), 75, 75)
sprites.add(player)

ticks = 0
runtime = True
while runtime:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            runtime = False
         
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                runtime = False
    
    screen.fill((53, 85, 108)) # fills a surface with the rgb color
    
    # updates
    sprites.draw(screen)
    sprites.update(sprites)
        
    # updates screen
    pygame.display.update()

    clock.tick(60)
    

# closes pygame application
pygame.quit()



#