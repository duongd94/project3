from home_page import Title


class HighScore:
    """Initialize hs"""
    def __init__(self, ai_settings, screen, game_stats):
        self.score_text = []
        self.score_text.append(Title(ai_settings.bg_color, screen, 'High Scores'))
        for num, value in enumerate(game_stats.hs_all, 1):
            self.score_text.append(Title(ai_settings.bg_color, screen, str(num) + '.   ' + str(value),
                                         text_color=(166, 130, 133)))

        # initialize hs list
        y_offset = ai_settings.screen_height * 0.05
        for text in self.score_text:
            text.prep_image()
            text.image_rect.centerx = ai_settings.screen_width // 2
            text.image_rect.centery = y_offset
            y_offset += ai_settings.screen_height * 0.05

    def display_scores(self):
        """display high score"""
        for text in self.score_text:
            text.blitme()
