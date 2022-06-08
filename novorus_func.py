import pygame, os, math

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords, width, height, image):
        super().__init__()
        self.name = 'player'
        self.x, self.y, = coords
        self.x_velocity, self.y_velocity = 0, 0
        self.width, self.height = width, height
        self.load_image(image)
        
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
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height).inflate_ip(90, 90)

    def handle_keys(self, frame, sprites):
        '''Handles events relating to the player'''
        self.movement(sprites)
        self.animation(frame)
    
    def collision(self, sprites):
        for sprite in sprites:
            collision_distance = [(self.width + sprite.width) / 2, (self.height + sprite.height) / 2,]
            player_center = [self.x + self.width / 2, self.y + self.height / 2]
            sprite_center = [sprite.x + sprite.width / 2, sprite.y + sprite.height / 2]
            distance = [player_center[i] - sprite_center[i] for i in range(2)]
            
            if abs(distance[0]) <= collision_distance[0] and abs(distance[1]) <= collision_distance[1]:
                if abs(distance[0]) > abs(distance[1]):
                    if distance[0] < 0:
                        self.x = sprite.rect.left - self.width
                        print('left')
                        
                    if distance[0] > 0: 
                        self.x = sprite.rect.right
                        print('right')
                    
                else:
                    if distance[1] > 0: 
                        self.y = sprite.rect.bottom
                        print('bottom')
                            
                    if distance[1] < 0: 
                        self.y = sprite.rect.top - self.width
                        print('up')
            
    def movement(self, sprites):
        '''Handles movement'''
        distance = 0.025 / 2
        max_speed = 0.5 / 2
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            if self.x_velocity > -max_speed:
                self.x_velocity -= distance * 0.9 ** abs(self.x_velocity)
                if self.x_velocity < -max_speed:
                    self.x_velocity == -max_speed
        
        elif keys[pygame.K_RIGHT]:
            if self.x_velocity < max_speed:
                self.x_velocity += distance * 0.9 ** abs(self.x_velocity)
                if self.x_velocity > max_speed:
                    self.x_velocity == max_speed
        
        # movement decay
        else:
            if self.x_velocity != 0:
                self.x_velocity *= 0.9
                if abs(self.x_velocity) < distance:
                    self.x_velocity = 0

        if keys[pygame.K_DOWN]:
            if self.y_velocity < max_speed:
                self.y_velocity += distance * 0.9 ** abs(self.y_velocity)
                if self.y_velocity > max_speed:
                    self.y_velocity == max_speed

        elif keys[pygame.K_UP]:
            if self.y_velocity > -max_speed:
                self.y_velocity -= distance * 0.9 ** abs(self.y_velocity)
                if self.y_velocity < -max_speed:
                    self.y_velocity == -max_speed
        
        # movement decay
        else:
            if self.y_velocity != 0:
                self.y_velocity *= 0.9
                if abs(self.y_velocity) < distance:
                    self.y_velocity = 0
        
        self.x += self.x_velocity
        self.y += self.y_velocity
        self.collision(sprites)
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    
    def animation(self, frame):
        '''Handles the animation of the player'''
        movement_sprites = ['knight_walk1.png', 'knight_walk2.png', 'knight_walk3.png']
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_UP]:
            self.load_image(movement_sprites[math.floor(frame / 100)])
            self.image = pygame.transform.flip(self.image, True, False)
            
        elif keys[pygame.K_RIGHT] or keys[pygame.K_DOWN]:
            self.load_image(movement_sprites[math.floor(frame / 100)])

class Wall(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'gray_bricks.png')
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
class Ghost(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'ghost.png')
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
class Chest(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'chest.png')
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)




