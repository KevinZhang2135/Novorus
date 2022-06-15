import pygame, os, math, random

class Sprite(pygame.sprite.Sprite):
    def __init__(self, size: list, group):
        super().__init__(group)
        self.width, self.height = size

    def load_image(self, image):
        '''Loads an image according to the input'''
        image = pygame.image.load(os.path.join('sprites', image)).convert_alpha()
        image = pygame.transform.scale(image, (self.width, self.height))
        
        return image

class Player(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        self.image = self.load_image('knight_walk1.png')
        self.rect = self.image.get_rect(center=coords)
        self.rect.inflate_ip(self.width * -0.3, 0)
        
        self.direction = pygame.math.Vector2()
        self.speed = 2
        
        self.facing = 'right'
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
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN] or keys[pygame.K_UP]:# or keys[pygame.K_UP]:
            self.image = self.load_image(movement_sprites[math.floor(self.ticks / 30)])

            if keys[pygame.K_LEFT]: 
                self.facing = 'left'
            
            elif keys[pygame.K_RIGHT]:
                self.facing = 'right' 

        else:
            self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])

        if self.facing == 'left':
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
        super().__init__(size, groups)
        self.image = self.load_image('ghost_idle1.png')
        self.rect = self.image.get_rect(center = coords)
        self.rect.inflate_ip(self.width * -0.3, self.height * -0.15)
        
        self.ticks = random.randint(0, 30)
    
    def animation(self):
        '''Handles animation'''
        idle_sprites = ['ghost_idle1.png', 'ghost_idle2.png', 'ghost_idle3.png', 'ghost_idle2.png']
        self.image = self.load_image(idle_sprites[math.floor(self.ticks / 30)])
        
    def update(self, sprites):
        '''Handles events'''
        self.animation()
        
        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
            
class Wall(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        self.image = self.load_image('gray_bricks.png')
        self.rect = self.image.get_rect(center = coords)
        
class Ambience(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self, ):
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
        '''Draws the screen according to player movement'''
        self.center_target(player)
        
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.bottom):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class HUDBackground:
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        ui_width = self.display_surface.get_width()
        ui_height = self.display_surface.get_height() // 9
        
        self.rect = pygame.Rect(
            (0, ui_height * 8),
            (ui_width, ui_height))
            
    def draw(self):
        brown = (104, 84, 66)
        pygame.draw.rect(self.display_surface, brown, self.rect, 0)
        
class Menu(Sprite):
    def __init__(self, coords: list, size: list, groups):
        super().__init__(size, groups)
        
pygame.init()
pygame.display.set_caption('Novorus')

screen = pygame.display.set_mode() # sets the size of the screen; defaults to full screen
clock = pygame.time.Clock()

camera_group = CameraGroup()
collision_group = pygame.sprite.Group()
hud_group = CameraGroup()

# ambience
size = [60, 40, 150]
objects = ['rock', 'grass', 'tree']
for i, obj in enumerate(objects):
    for j in range(25 + 25 * i):
        coords = [random.randint(0, 2000), random.randint(0, 2000)]
        decor = Ambience(coords, (size[i], size[i]), camera_group)

        variation = random.randint(1, 3)
        decor.image = decor.load_image(f'{obj}{variation}.png')
        decor.rect = decor.image.get_rect(center = coords)
        if random.randint(0, 1):
            decor.image = pygame.transform.flip(decor.image, True, False)

# enemies
size = [75, 75]
for i in range(1):
    coords = [random.randint(0, 2000), random.randint(0, 2000)]
    ghost = Ghost(coords, size, (camera_group, collision_group))
        
# player
coords = [1000, 1000]
size = [75, 75]
player = Player(coords, size, camera_group)

# hud
hud_bg = HUDBackground()

ticks = 0
state = 'running'
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
    
    screen.fill((130, 200, 90)) # fills a surface with the rgb color
    
    # updates
    camera_group.custom_draw(player)
    hud_bg.draw()
    
    #camera_group.draw(screen)
    if state != 'paused':
        camera_group.update(collision_group)
    
    # updates screen
    pygame.display.update()
    clock.tick(60)
    

# closes pygame application
pygame.quit()