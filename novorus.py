import pygame

class Sprite(pygame.sprite.Sprite):
  def __init__(self, color, width, height):
    super().__init__()
  
    self.image = pygame.Surface([width, height])
    self.image.fill(color)
  
    pygame.draw.rect(self.image, 
                     color, 
                     pygame.Rect(50, 50, width, height))
  
    self.rect = self.image.get_rect()


pygame.init()

screen = pygame.display.set_mode() # sets the dimensions of the screen; defaults to full screen

sprites = pygame.sprite.Group()
player = Sprite((200, 200, 200), 100, 100)
sprites.add(player)


runtime = True
while runtime:
  
  for event in pygame.event.get():
    # checks for quit event
    if event.type == pygame.QUIT:
      runtime = False
      
    if event.type == pygame.KEYDOWN:
      x, y = 0, 0
      keys = pygame.key.get_pressed()
      if keys[pygame.K_LEFT]:
        x -= 5
        
      if keys[pygame.K_RIGHT]:
        x += 5
        
      if keys[pygame.K_DOWN]:
        y -= 5
        
      if keys[pygame.K_UP]:
        y += 5
        
      player.move(x, y)
  
  screen.fill((53, 85, 108)) # fills a surface with the rgb color
  
  # updates sprites
  sprites.update() 
  sprites.draw(screen)
  
  pygame.display.flip() # updates screen
  
# closes pygame application
pygame.quit()


