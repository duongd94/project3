import json


class GameStats:
    """Track and store stats by using json"""
    def __init__(self, ai_settings):
        self.ai_settings = ai_settings
        self.ships_left = 0
        self.aliens_start = None
        self.next_speedup = None
        self.aliens_left = None
        self.hs = None
        self.hs_all = None
        self.score = None
        self.level = None
        self.reset_stats()
        self.initialize_hs()
        self.game_active = False

    def initialize_hs(self):
        """read stored stats"""
        try:
            with open('score_data.json', 'r') as file:
                self.hs_all = json.load(file)
                self.hs_all.sort(reverse=True)
                self.hs = self.hs_all[0]
        except (FileNotFoundError, ValueError, EOFError, json.JSONDecodeError, AttributeError, IndexError) as e:
            print(e)
            self.hs_all = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.hs = self.hs_all[0]

    def save_hs(self):
        """Save stats"""
        for i in range(len(self.hs_all)):
            if self.score >= self.hs_all[i]:
                self.hs_all[i] = self.score
                break
        with open('score_data.json', 'w') as file:
            json.dump(self.hs_all, file)

    def reset_stats(self):
        """reset stats"""
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 1
