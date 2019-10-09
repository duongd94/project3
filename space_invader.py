import pygame
import game_fuctions as gf

from ship import Ship
from settings import Settings
from scoreboard import Scoreboard
from bunker import create_bunker
from game_stats import GameStats


def run():
    # Setup pygame, display and settings
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Space_Invader")
    clock = pygame.time.Clock()

    # Stats
    stats = GameStats(ai_settings)

    # Scoreboard
    sb = Scoreboard(ai_settings, screen, stats)

    # Ship, bullets, aliens, beam
    ship = Ship(ai_settings, screen)
    bullets = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    beams = pygame.sprite.Group()
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # UFO, bunker
    ufo = pygame.sprite.Group()
    bunkers = pygame.sprite.Group(create_bunker(ai_settings, screen, 0),
                                  create_bunker(ai_settings, screen, 1),
                                  create_bunker(ai_settings, screen, 2),
                                  create_bunker(ai_settings, screen, 3))

    while True:
        # fps
        clock.tick(60)
        if not stats.game_active:
            quit_game = not gf.startup(ai_settings, stats, screen)
            if quit_game:
                pygame.quit()
                break
            gf.new_game(ai_settings, screen, stats, sb, ship, aliens, beams, bullets)
        gf.check_events(ai_settings, screen, stats, ship, bullets)
        if stats.game_active:
            ship.update()
            gf.update_aliens(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)
            gf.update_bullets_beams(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)

        gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, bunkers, ufo)
        gf.bg_music(ai_settings, stats)


if __name__ == '__main__':
    run()
