import pygame, os, math, random

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords: list, width, height, image):
        super().__init__()
        self.x, self.y, = coords
        self.width, self.height = width, height

        self.load_image(image)
        self.rect = self.image.get_rect(midbottom = (self.x + self.width / 2, self.y + self.height))
        
        self.direction = pygame.math.Vector2()
        
    def load_image(self, image):
        '''Loads an image according to the input'''
        self.image = pygame.image.load(os.path.join('sprites', image)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

class Player(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'knight_walk1.png')
        self.ticks = 0

    def update(self, sprites):
        '''Handles events relating to the player'''
        self.movement(sprites)
        self.animation(self.ticks)

        self.ticks += 1
        if self.ticks >= 120:
            self.ticks = 0
    
    def collision(self, sprites):
        '''Handles collision'''
        for sprite in sprites:
            collision_distance = [(self.width + sprite.width) / 2, (self.height + sprite.height) / 2,]
            distance = [self.rect.center[i] - sprite.rect.center[i] for i in range(2)]
            
            # checks if the distance of the sprites are within collision distance
            if abs(distance[0]) <= collision_distance[0] and abs(distance[1]) <= collision_distance[1]:
                # horizontal collision
                if abs(distance[0]) > abs(distance[1]):
                    # left collision
                    if distance[0] < 0:
                        self.x = sprite.rect.left - self.width
                        
                    # right collision
                    if distance[0] > 0: 
                        self.x = sprite.rect.right
                
                # vertical collision
                else:
                    # bottom collision
                    if distance[1] > 0: 
                        self.y = sprite.rect.bottom
                    
                    # up collision
                    if distance[1] < 0: 
                        self.y = sprite.rect.top - self.width

    def movement(self, sprites):
        '''Handles movement'''
        speed = 2
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.direction.x = -speed
        
        elif keys[pygame.K_RIGHT]:
            self.direction.x = speed
        
        # movement decay
        else:
            self.direction.x = 0

        if keys[pygame.K_DOWN]:
            self.direction.y = speed

        elif keys[pygame.K_UP]:
            self.direction.y = -speed
        
        # movement decay
        else:
            self.direction.y = 0

        self.collision(sprites)
        self.x += self.direction.x
        self.y += self.direction.y
    
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    
    def animation(self, ticks):
        '''Handles the animation of the player'''
        movement_sprites = ['knight_walk1.png', 'knight_walk2.png', 'knight_walk1.png', 'knight_walk3.png']
        idle_sprites = ['knight_walk1.png', 'knight_idle1.png', 'knight_walk1.png', 'knight_idle2.png']

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:# or keys[pygame.K_UP]:
            self.load_image(movement_sprites[math.floor(ticks / 30)])

        else:
            self.load_image(idle_sprites[math.floor(ticks / 30)])

        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

class Wall(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'gray_bricks.png')
               
class Ghost(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'ghost.png')
        
class Chest(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'chest.png')




