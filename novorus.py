import pygame, os, math

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords, width, height, image):
        self.name = 'player'
        self.x, self.y, = coords
        self.width, self.height = width, height
        
        super().__init__()
        self.load_image(image)
        self.rect = self.image.get_rect()
        
    def load_image(self, image):
        '''Loads an image according to the input'''
        self.image = pygame.image.load(os.path.join('sprites', image))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self, surface):
        '''Redraws the player every frame'''
        surface.blit(self.image, (self.x, self.y))

class Player(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'knight_walk1.png')

    def handle_keys(self, frame, sprites):
        '''Handles events relating to the player'''
        self.movement()
        self.animation(frame)
    
    def movement(self):
        '''Handles movement'''
        distance = 0.75
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.x -= distance
        
        elif keys[pygame.K_RIGHT]:
            self.x += distance
              
        if keys[pygame.K_DOWN]:
            self.y += distance
          
        elif keys[pygame.K_UP]:
            self.y -= distance
            
    def collision(self):
        if not self.rect.collidepoint(100, 100):
            pass
    
    def animation(self, frame):
        '''Handles the animation of the player'''
        movement_sprites = ['knight_walk1.png', 'knight_walk2.png', 'knight_walk3.png']
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.load_image(movement_sprites[math.floor(frame / 75)])
            self.image = pygame.transform.flip(self.image, True, False)
            
        elif keys[pygame.K_RIGHT]:
            self.load_image(movement_sprites[math.floor(frame / 75)])

class Wall(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'brick_wall.png')
        
class Ghost(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'ghost.png')

pygame.init()
screen = pygame.display.set_mode() # sets the dimensions of the screen; defaults to full screen
pygame.display.set_caption('Novorus')

sprites = pygame.sprite.Group()

for i in range(0, 300, 200):
    ghost = Ghost((i, 0), 100, 100)    
    sprites.add(ghost)
    
player = Player((300, 0), 100, 100)


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
    sprites.update()
    
    player.handle_keys(frame, sprites.sprites)
    player.draw(screen)
    
    for sprite in sprites.sprites():
        sprite.draw(screen)
        
    # updates screen
    pygame.display.flip() 

    frame += 1
    if frame >= 225:
        frame = 0


# closes pygame application
pygame.quit()







