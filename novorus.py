import pygame
from novorus_func import *

pygame.init()
screen = pygame.display.set_mode() # sets the dimensions of the screen; defaults to full screen
pygame.display.set_caption('Novorus')

all_sprites = pygame.sprite.Group()

for i in range(0, 300, 200):
    ghost = Ghost((i, 100), 75, 75)    
    all_sprites.add(ghost)
    
for i in range(0, 500, 100):
    wall = Wall((i, 300), 100, 100)    
    all_sprites.add(wall)
    
chest = Chest((300, 200), 80, 80)
all_sprites.add(chest)
    
player = Player((300, 0), 75, 75)

frame = 0
runtime = True

while runtime:
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            runtime = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        runtime = False
    
    screen.fill((53, 85, 108)) # fills a surface with the rgb color
    
    # updates
    player.handle_keys(frame, all_sprites)
    player.draw(screen)
    pygame.draw.rect(screen, (255, 0, 0), player.rect, 1)
    
    for sprite in all_sprites.sprites():
        sprite.draw(screen)
        pygame.draw.rect(screen, (255, 0, 0), sprite.rect, 1)
        
    # updates screen
    pygame.display.flip() 

    frame += 1
    if frame >= 300:
        frame = 0

# closes pygame application
pygame.quit()



#