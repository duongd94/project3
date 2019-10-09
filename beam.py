import pygame


class Beam(pygame.sprite.Sprite):
    """Initialize beam"""
    def __init__(self, ai_settings, screen, alien):
        super().__init__()
        self.screen = screen

        # set beam
        self.image = pygame.image.load('images/alien_beam_resized.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = alien.rect.centerx
        self.rect.top = alien.rect.bottom

        self.y = float(self.rect.y)
        self.speed_factor = ai_settings.beam_speed_factor

    def update(self):
        """update beam"""
        self.y += self.speed_factor
        self.rect.y = self.y

    def blitme(self):
        """display beam"""
        self.screen.blit(self.image, self.rect)