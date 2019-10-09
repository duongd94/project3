import sys
import pygame
import random

from alien import Alien
from bullet import Bullet
from beam import Beam
from high_scores import HighScore
from home_page import Button, Intro, new_level
from ufo import UFO


def check_events(ai_settings, screen, stats, ship, bullets):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stats.save_hs()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats.game_active, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)


def new_game(ai_settings, screen, stats, sb, ship, aliens, beams, bullets):
    """Starting new game"""
    # make mouse invisible
    pygame.mouse.set_visible(False)

    # reset the game
    stats.reset_stats()
    stats.game_active = True
    sb.prep_score()
    sb.prep_hs()
    sb.prep_level()
    sb.prep_ships()

    # delete aliens, bullets, beams
    aliens.empty()
    bullets.empty()
    beams.empty()

    # reset alien fleet and ship
    create_fleet(ai_settings, screen, ship, aliens)
    stats.next_speedup = len(aliens) - (len(aliens) // 5)
    stats.aliens_left = len(aliens)
    ship.center_ship()


def startup(ai_settings, game_stats, screen):
    """Set and display the startup menu"""
    menu = Intro(ai_settings, game_stats, screen)
    play_button = Button(ai_settings, screen, 'Play Game', y_factor=0.70)
    hs_button = Button(ai_settings, screen, 'High Scores', y_factor=0.80)
    intro = True

    while intro:
        play_button.alter_text_color(*pygame.mouse.get_pos())
        hs_button.alter_text_color(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_x, click_y = pygame.mouse.get_pos()
                game_stats.game_active = play_button.check_button(click_x, click_y)
                intro = not game_stats.game_active
                if hs_button.check_button(click_x, click_y):
                    ret_hs = hs_screen(ai_settings, game_stats, screen)
                    if not ret_hs:
                        return False

        screen.fill(ai_settings.bg_color)
        menu.show_menu()
        hs_button.draw_button()
        play_button.draw_button()
        pygame.display.flip()

    return True


def check_keydown_events(event, ai_settings, screen, game_active, ship, bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE and game_active:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def alien_collision_check(bullet, alien):
    if alien.dead:
        return False
    return pygame.sprite.collide_rect(bullet, alien)


def check_alien_bullet_collisions(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo):
    """check collision and handle new level"""
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, False, collided=alien_collision_check)
    if collisions:
        for aliens_hit in collisions.values():
            for a in aliens_hit:
                stats.score += ai_settings.alien_points[str(a.alien_type)]
                a.begin_death()
            sb.prep_score()
        check_hs(stats, sb)

    ufo_collide = pygame.sprite.groupcollide(bullets, ufo, True, False, collided=alien_collision_check)

    if ufo_collide:
        for ufo in ufo_collide.values():
            for u in ufo:
                stats.score += u.score
                u.begin_death()
            sb.prep_score()
        check_hs(stats, sb)
    if len(aliens) == 0:
        # starting new level
        if ufo:
            for u in ufo.sprites():
                u.kill()
        beams.empty()
        bullets.empty()
        stats.level += 1
        new_level(ai_settings, screen, stats)
        ai_settings.increase_base_speed()
        ai_settings.reset_alien_speed()
        sb.prep_level()
        create_fleet(ai_settings, screen, ship, aliens)
        stats.next_speedup = len(aliens) - (len(aliens) // 5)

    stats.aliens_left = len(aliens)

    if stats.aliens_left <= stats.next_speedup and ai_settings.alien_speed_factor < ai_settings.alien_speed_limit:
        ai_settings.increase_alien_speed()
        stats.next_speedup = stats.aliens_left - (stats.aliens_left // 5)


def check_ship_beam_collisions(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo):
    """Check ship been hit"""
    collide = pygame.sprite.spritecollideany(ship, beams)
    if collide:
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)


def check_bunker_collisions(beams, bullets, bunkers):
    """Check bunkers been hit"""
    collisions = pygame.sprite.groupcollide(bullets, bunkers, True, False)
    for bunkers_list in collisions.values():
        for block in bunkers_list:
            block.damage(top=False)
    collisions = pygame.sprite.groupcollide(beams, bunkers, True, False)
    for bunkers_list in collisions.values():
        for block in bunkers_list:
            block.damage(top=True)


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, beams, ufo):
    """check collision"""
    if ufo:
        for u in ufo.sprites():
            u.kill()
    ship.death()
    ship.update()

    while ship.dead:
        screen.fill(ai_settings.bg_color)
        ship.blitme()
        pygame.display.flip()
        ship.update()

    if stats.ships_left > 0:
        stats.ships_left -= 1
        # reset when collision occur
        aliens.empty()
        bullets.empty()
        beams.empty()
        ai_settings.reset_alien_speed()
        create_fleet(ai_settings, screen, ship, aliens)
        stats.next_speedup = len(aliens) - (len(aliens) // 5)
        stats.aliens_left = len(aliens.sprites())
        ship.center_ship()

        # Update sb
        sb.prep_ships()
    else:
        ai_settings.stop_bgm()
        pygame.mixer.music.load('sounds/endgame.wav')
        pygame.mixer.music.play()

        stats.game_active = False
        stats.save_hs()
        pygame.mouse.set_visible(True)


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_limit:
        new_bullet = Bullet(ai_settings, screen, ship)
        ship.fire_weapon()
        bullets.add(new_bullet)


def fire_random_beam(ai_settings, screen, aliens, beams):
    """Fire a beam from aliens"""
    attack = random.choice(aliens.sprites())
    if len(beams) < ai_settings.beams_limit and \
            (ai_settings.beam_stamp is None or
             (abs(pygame.time.get_ticks() - ai_settings.beam_stamp) > ai_settings.beam_time)):
        new_beam = Beam(ai_settings, screen, attack)
        attack.fire_weapon()
        beams.add(new_beam)


def get_number_aliens(ai_settings, alien_width):
    """set aliens"""
    available_space_x = ai_settings.screen_width - 3 * alien_width
    number_aliens_x = int(available_space_x / (2.5 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """set rows"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create and set aliens"""
    if row_number < 2:
        alien_type = 1
    elif row_number < 4:
        alien_type = 2
    else:
        alien_type = 3

    alien = Alien(ai_settings, screen, alien_type)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 1.5 * alien.rect.height * row_number
    alien.rect.y += int(ai_settings.screen_height / 6)
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Creates and set fleets"""
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def change_fleet_direction(ai_settings, aliens):
    """handle fleet's movement"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def check_fleet_edges(ai_settings, aliens):
    """handle edges"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def create_random_ufo(ai_settings, screen):
    """randomly create ufo"""
    ufo = None

    if random.randrange(0, 100) <= 15:
        ufo = UFO(ai_settings, screen)
    time_stamp = pygame.time.get_ticks()
    return time_stamp, ufo


def ufo_event_check(ai_settings, screen, ufo_group):
    """handle ufo spawn"""
    if not ai_settings.last_ufo and not ufo_group:
        ai_settings.last_ufo, new_ufo = create_random_ufo(ai_settings, screen)
        if new_ufo:
            ufo_group.add(new_ufo)
    elif abs(pygame.time.get_ticks() - ai_settings.last_ufo) > ai_settings.ufo_min_interval and not ufo_group:
        ai_settings.last_ufo, new_ufo = create_random_ufo(ai_settings, screen)
        if new_ufo:
            ufo_group.add(new_ufo)


def update_bullets_beams(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo):
    """Update and reset bullets/beams"""
    bullets.update()
    beams.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    for beam in beams.copy():
        if beam.rect.bottom > ai_settings.screen_height:
            beams.remove(beam)
    check_alien_bullet_collisions(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)
    check_ship_beam_collisions(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)


def check_hs(stats, sb):
    """Check new high score."""
    if stats.score > stats.hs:
        stats.high_score = stats.score
        sb.prep_hs()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, beams,
                  bullets, bunkers, ufo_group):
    """Update screen"""
    if stats.game_active:
        ufo_event_check(ai_settings, screen, ufo_group)
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    for beam in beams.sprites():
        beam.blitme()
    if ufo_group:
        ufo_group.update()
        for ufo in ufo_group.sprites():
            ufo.blitme()

    aliens.draw(screen)
    check_bunker_collisions(beams, bullets, bunkers)
    sb.show_score()
    ship.blitme()
    bunkers.update()
    pygame.display.flip()


def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo):
    """Check if any aliens have reached the bottom"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)
            break


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo):
    """Check aliens position"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)

    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, beams, bullets, ufo)
    if aliens.sprites():
        fire_random_beam(ai_settings, screen, aliens, beams)


def hs_screen(ai_settings, game_stats, screen):
    """Display hs"""
    hs = HighScore(ai_settings, screen, game_stats)
    back_button = Button(ai_settings, screen, 'Back To Menu', y_factor=0.85)

    while True:
        back_button.alter_text_color(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_button(*pygame.mouse.get_pos()):
                    return True

        screen.fill(ai_settings.bg_color)
        hs.display_scores()
        back_button.draw_button()
        pygame.display.flip()


def bg_music(ai_settings, stats):
    """Play back ground music"""
    if stats.game_active:
        ai_settings.continue_bgm()
