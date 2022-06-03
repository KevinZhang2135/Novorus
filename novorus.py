import pygame, os

class Sprite(pygame.sprite.Sprite):
  def __init__(self, coords, width, height, image):
    self.x, self.y, = coords
    self.state = 0
    self.width, self.height = width, height
    super().__init__()
  
    self.load_image(image)
    self.rect = self.image.get_rect()

  def draw(self, surface):
    '''Redraws the player every frame'''
    surface.blit(self.image, (self.x, self.y))

class Player(Sprite):
  def __init__(self, coords, width, height):
    super().__init__(coords, width, height, 'knight_walk_right1.png')

  def load_image(self, image):
    '''Loads an image according to the input'''
    self.image = pygame.image.load(os.path.join('sprites', image))
    self.image = pygame.transform.scale(self.image, (self.width, self.height))

  def handle_keys(self):
    '''Handles events relating to the player'''
    distance = 0.75 * 5
    state_interval = 75

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN] or keys[pygame.K_UP]:
      self.state += 1

    if keys[pygame.K_LEFT]:
      self.x -= distance
      if self.state <= state_interval:
        self.load_image('knight_walk_left1.png')

      elif self.state > state_interval and self.state <= state_interval * 2:
        self.load_image('knight_walk_left2.png')
      
      else:
        self.load_image('knight_walk_left3.png')
    
    elif keys[pygame.K_RIGHT]:
      self.x += distance
      if self.state <= state_interval:
        self.load_image('knight_walk_right1.png')

      elif self.state > state_interval and self.state <= state_interval * 2:
        self.load_image('knight_walk_right2.png')

      else:
        self.load_image('knight_walk_right3.png')
      
    if keys[pygame.K_DOWN]:
      self.y += distance
      
    elif keys[pygame.K_UP]:
      self.y -= distance

    if self.state >= state_interval * 3:
      self.state = 0

class Wall(Sprite):
  def __init__(self, coords, width, height):
    super().__init__(coords, width, height, 'wall.png')

pygame.init()
screen = pygame.display.set_mode() # sets the dimensions of the screen; defaults to full screen
pygame.display.set_caption('Novorus')

walls = []
for i in range(1):
  pass
player = Player((300, 0), 200, 200)

sprites = pygame.sprite.Group()
sprites.add(player)

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
  sprites.update() 
  player.handle_keys()
  player.draw(screen)

  pygame.display.flip() # updates screen


  
  
# closes pygame application
pygame.quit()


