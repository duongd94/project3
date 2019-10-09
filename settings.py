import pygame

from pygame import mixer
from pygame import time


class Settings:
    """Init. setting"""
    def __init__(self):
        pygame.init()
        # screen
        self.screen_width = 1200
        self.screen_height = 800
        print('Automatic screen resolution: ' + str(self.screen_width) + ' ' + str(self.screen_height))
        self.bg_color = (0, 0, 0)

        # ship
        self.ship_speed_factor = None
        self.ship_limit = 3

        # bullets
        self.bullet_speed_factor = None
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 255, 255)
        self.bullets_limit  = 5

        # bunker
        self.bunker_block_size = 10
        self.bunker_color = (255, 239, 213)

        # beams
        self.beam_speed_factor = None
        self.beams_limit = 3

        # sound
        self.audio_channels = 5
        self.ship_channel = pygame.mixer.Channel(0)
        self.alien_channel = pygame.mixer.Channel(1)
        self.death_channel = pygame.mixer.Channel(2)
        self.ufo_channel = pygame.mixer.Channel(3)
        self.music_channel = pygame.mixer.Channel(4)
        self.normal_music_interval = 725
        self.music_interval = self.normal_music_interval
        self.music_speedup = 25
        self.bgm = [
            pygame.mixer.Sound('sounds/bgm1.wav'),
            pygame.mixer.Sound('sounds/bgm2.wav'),
            pygame.mixer.Sound('sounds/bgm3.wav'),
            pygame.mixer.Sound('sounds/bgm4.wav')
             ]
        self.bgm_index = None
        self.last_beat = None

        # alien
        self.normal_alien_speed = 2
        self.alien_speed_limit = None
        self.alien_base_limit = None
        self.alien_speed_factor = None
        self.ufo_speed = None
        self.last_ufo = None
        self.ufo_min_interval = 10000
        self.fleet_drop_speed = 10
        self.fleet_direction = None
        self.alien_points = None
        self.ufo_point_values = [50, 100, 150]
        self.beam_stamp = None
        self.beam_time = 1000

        # increase speed
        self.speedup_scale = 1.1

        # game dynamic settings
        self.initialize_dynamic_settings()
        self.initialize_audio_settings()

    def initialize_dynamic_settings(self):
        """Initialize dynamic setting"""
        self.ship_speed_factor = 8
        self.bullet_speed_factor = 15
        self.beam_speed_factor = 5
        self.alien_speed_factor = self.normal_alien_speed
        self.alien_speed_limit = self.alien_speed_factor * 5
        self.alien_base_limit = self.alien_speed_limit / 2
        self.ufo_speed = self.alien_speed_factor * 2

        # scoring for diff aliens
        self.alien_points = {'1': 10, '2': 20, '3': 40}

        # fleet direction
        self.fleet_direction = 1

    def initialize_audio_settings(self):
        """sound settings"""
        mixer.init()
        mixer.set_num_channels(self.audio_channels)
        self.music_channel.set_volume(0.7)

    def continue_bgm(self):
        """set bgm"""
        if not self.last_beat:
            self.bgm_index = 0
            self.music_channel.play(self.bgm[self.bgm_index])
            self.last_beat = time.get_ticks()
        elif abs(self.last_beat - time.get_ticks()) > self.music_interval and not self.music_channel.get_busy():
            self.bgm_index = (self.bgm_index + 1) % len(self.bgm)
            self.music_channel.play(self.bgm[self.bgm_index])
            self.last_beat = time.get_ticks()

    def stop_bgm(self):
        """Stop bgm"""
        self.music_channel.stop()
        self.last_beat = None
        self.bgm_index = None

    def increase_base_speed(self):
        """change aliens' speed"""
        if self.normal_alien_speed < self.alien_base_limit:
            self.normal_alien_speed *= self.speedup_scale
            self.normal_music_interval -= self.music_speedup

    def increase_alien_speed(self):
        """Increase aliens' speed, adjust music"""
        self.alien_speed_factor *= self.speedup_scale
        self.music_interval -= self.music_speedup

    def reset_alien_speed(self):
        """Reset alien"""
        self.alien_speed_factor = self.normal_alien_speed
        self.music_interval = self.normal_music_interval
