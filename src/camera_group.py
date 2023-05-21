import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game = game

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_width() / 2
        self.half_height = self.display_surface.get_height() / 2

        self.texts = []

    def center_target(self, target):
        self.offset.x = 0
        self.offset.y = 0

        # stops scrolling screen when the player is past right edge of the screen
        if (target.rect.centerx >= self.game.level.size.x - self.half_width):
            self.offset.x = self.game.level.size.x - self.display_surface.get_width()
        
        # starts scrolling screen when the player is in the middle of the screen
        elif (target.rect.centerx > self.half_width):
            self.offset.x = target.rect.centerx - self.half_width

        # stops scrolling screen when the player is past bottom edge of the screen
        if (target.rect.centery >= self.game.level.size.y - self.half_height):
            self.offset.y = self.game.level.size.y - self.display_surface.get_height()

        # starts scrolling screen when the player is in the middle of the screen
        elif (target.rect.centery > self.half_height):
            self.offset.y = target.rect.centery - self.half_height

    def custom_draw(self, player, show_hitboxes=False):
        '''Draws the screen according to player movement'''
        self.center_target(player)
        # sorts sprites by sprite layer as primary and rectangle bottom as secondary
        for sprite in sorted(self.sprites(), key=lambda sprite: (sprite.sprite_layer, sprite.rect.bottom)):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if show_hitboxes:
                hitbox = pygame.Rect(
                    sprite.rect.x - self.offset.x,
                    sprite.rect.y - self.offset.y,
                    sprite.rect.width,
                    sprite.rect.height)

                pygame.draw.rect(
                    self.display_surface,
                    (255, 0, 0),
                    hitbox,
                    1)

        expired_texts = []
        for index, text in enumerate(self.texts):
            if text.alpha <= 0:
                expired_texts.append(index)

            text.update()
            offset_pos = text.rect.topleft - self.offset
            self.display_surface.blit(text.text, offset_pos)

        # removes texts that have expired
        expired_texts.sort(reverse=True)
        for index in expired_texts:
            expired_text = self.texts.pop(index)
            del expired_text

    def update(self):
        "Updates all sprites"
        for sprite in self.sprites():
            if (abs(self.game.player.rect.centerx
                    - sprite.rect.centerx
                    + sprite.rect.width) < self.half_width

                or abs(self.game.player.rect.centery
                       - sprite.rect.centery
                       + sprite.rect.height) < self.half_height):

                sprite.update()
