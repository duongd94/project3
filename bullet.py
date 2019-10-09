import pygame


class Bullet(pygame.sprite.Sprite):
    """handle bullet"""

    def __init__(self, ai_settings, screen, ship):
        """initialize bullet."""
        super().__init__()
        self.screen = screen

        # set bullet's position
        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width, ai_settings.bullet_height)
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top

        # Store bullet's position
        self.y = float(self.rect.y)

        self.color = ai_settings.bullet_color
        self.speed_factor = ai_settings.bullet_speed_factor

    def update(self):
        """update bullet"""
        self.y -= self.speed_factor
        self.rect.y = self.y

    def draw_bullet(self):
        """Display bullet"""
        pygame.draw.rect(self.screen, self.color, self.rect)