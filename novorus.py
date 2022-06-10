import pygame, os, math, random

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords: list, size: list, group):
        super().__init__(group)
        self.width, self.height = size

    def load_image(self, image):
        '''Loads an image according to the input'''
        self.image = pygame.image.load(os.path.join('sprites', image)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

class Player(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(coords, size, groups)
        self.load_image('knight_walk1.png')
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(self.width * -0.3, 0)
        
        self.direction = pygame.math.Vector2()
        self.speed = 2
        
        self.ticks = 0

    def collision(self, sprites):
        '''Handles collision'''
        for sprite in sprites:
            collision_distance = [(self.rect.width + sprite.rect.width) / 2, (self.rect.height + sprite.rect.height) / 2,]
            distance = [self.rect.center[i] - sprite.rect.center[i] for i in range(2)]
            
            # checks if the distance of the sprites are within collision distance
            if abs(distance[0]) <= collision_distance[0] and abs(distance[1]) <= collision_distance[1]:
                # horizontal collision
                if abs(distance[0]) > abs(distance[1]):
                    # left collision
                    if distance[0] > 0: 
                        self.rect.left = sprite.rect.right
                    
                    # right collision
                    if distance[0] < 0:
                        self.rect.right = sprite.rect.left
                
                # vertical collision
                else:
                    # bottom collision
                    if distance[1] < 0: 
                        self.rect.bottom = sprite.rect.top
                    
                    # top collision
                    if distance[1] > 0: 
                        self.rect.top = sprite.rect.bottom
                    
                    

    def movement(self):
        '''Handles movement'''
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -self.speed
        
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = self.speed
        
        # movement decay
        else:
            self.direction.x = 0

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = self.speed

        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -self.speed
        
        # movement decay
        else:
            self.direction.y = 0

        self.rect.center += self.direction * self.speed
                    
    def animation(self):
        '''Handles animation'''
        movement_sprites = ['knight_walk1.png', 'knight_walk2.png', 'knight_walk1.png', 'knight_walk3.png']
        idle_sprites = ['knight_walk1.png', 'knight_idle1.png', 'knight_walk1.png', 'knight_idle2.png']

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:# or keys[pygame.K_UP]:
            self.load_image(movement_sprites[math.floor(self.ticks / 30)])

        else:
            self.load_image(idle_sprites[math.floor(self.ticks / 30)])

        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def attack(self, ticks):
        pass
    
    def update(self, sprites):
        '''Handles events'''
        self.movement()
        self.collision(sprites)

        self.animation()

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
               
class Ghost(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(coords, size, groups)
        self.load_image('ghost_idle1.png')
        self.rect = self.image.get_rect(center = coords)
        self.rect.inflate_ip(self.width * -0.3, self.height * -0.15)
        
        self.ticks = random.randint(0, 30)
    
    def animation(self):
        '''Handles animation'''
        idle_sprites = ['ghost_idle1.png', 'ghost_idle2.png', 'ghost_idle3.png', 'ghost_idle2.png']
        self.load_image(idle_sprites[math.floor(self.ticks / 30)])
        
    def update(self, sprites):
        '''Handles events'''
        self.animation()
        
        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
            
class Wall(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(coords, size, groups)
        self.load_image('gray_bricks.png')
        self.rect = self.image.get_rect(center = coords)
        
class Ambience(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(coords, size, groups)
            
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        
        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        
    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height
        
    def custom_draw(self, player):
        # draws the screen according to player movement
        self.center_target(player)
        
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

pygame.init()
pygame.display.set_caption('Novorus')

screen = pygame.display.set_mode() # sets the size of the screen; defaults to full screen
clock = pygame.time.Clock()

camera_group = CameraGroup()
enemies = pygame.sprite.Group()

size = [75, 75]
for i in range(10):
    coords = [random.randint(0, 500), random.randint(0, 500)]
    ghost = Ghost(coords, size, (camera_group, enemies))

size = [50, 50]
for i in range(25):
    coords = [random.randint(0, 1000), random.randint(0, 1000)]
    decor = Ambience(coords, size, camera_group)
    if i % 2:
        decor.load_image('grass1.png')
        
    else:    
        decor.load_image('grass2.png')
          
    decor.rect = decor.image.get_rect(center = coords)

size = [35, 35]
for i in range(10):
    coords = [random.randint(0, 1000), random.randint(0, 1000)]
    decor = Ambience(coords, size, camera_group)
    decor.load_image('rock1.png')
        
    decor.rect = decor.image.get_rect(center = coords)

size = [125, 125]
for i in range(20):
    coords = [random.randint(0, 1000), random.randint(0, 1000)]
    decor = Ambience(coords, size, camera_group)
    decor.load_image('tree1.png')    
    decor.rect = decor.image.get_rect(center = coords)    
        
coords = [500, 500]
size = [75, 75]
player = Player(coords, size, camera_group)

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
    
    screen.fill((111, 177, 70)) # fills a surface with the rgb color
    
    # updates
    camera_group.custom_draw(player)
    #camera_group.draw(screen)
    camera_group.update(enemies)
        
    # updates screen
    pygame.display.update()
    clock.tick(60)
    

# closes pygame application
pygame.quit()



#


