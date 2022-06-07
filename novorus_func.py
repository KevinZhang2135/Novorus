import pygame, os, math

class Sprite(pygame.sprite.Sprite):
    def __init__(self, coords, width, height, image):
        self.name = 'player'
        self.x, self.y, = coords
        self.x_velocity, self.y_velocity = 0, 0
        self.width, self.height = width, height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        super().__init__()
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

    def handle_keys(self, frame, sprites):
        '''Handles events relating to the player'''
        self.movement(sprites)
        self.animation(frame)
    
    def movement(self, sprites):
        '''Handles movement'''
        distance = 0.025
        max_speed = 0.5
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

        else:
            if self.y_velocity != 0:
                self.y_velocity *= 0.9
                if abs(self.y_velocity) < distance:
                    self.y_velocity = 0
        
        can_go = self.collision(sprites)
        if can_go['left'] and self.x_velocity <= 0:
            self.x += self.x_velocity
        
        if can_go['right'] and self.x_velocity >= 0:
            self.x += self.x_velocity

        if can_go['down'] and self.y_velocity >= 0:
            self.y += self.y_velocity
        
        if can_go['up'] and self.y_velocity <=0:
            self.y += self.y_velocity
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
    def collision(self, sprites):
        can_go = {'left': True,
                  'right': True,
                  'down': True,
                  'up': True}

        for sprite in sprites:
            if sprite.rect.collidepoint(self.rect.left, self.rect.top) or sprite.rect.collidepoint(self.rect.left, self.rect.bottom):
               can_go['left'] = False

            if sprite.rect.collidepoint(self.rect.right, self.rect.top) or sprite.rect.collidepoint(self.rect.right, self.rect.bottom):
                can_go['right'] = False

            if sprite.rect.collidepoint(self.rect.left, self.rect.bottom) or sprite.rect.collidepoint(self.rect.right, self.rect.bottom):
                can_go['down'] = False
            
            if sprite.rect.collidepoint(self.rect.left, self.rect.top) or sprite.rect.collidepoint(self.rect.right, self.rect.top):
                can_go['up'] = False

        return can_go
                    
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
        super().__init__(coords, width, height, 'brick_wall.png')
        
class Ghost(Sprite):
    def __init__(self, coords, width, height):
        super().__init__(coords, width, height, 'ghost.png')
