from unittest import TestCase

from ..day_game_info_api import DayGameInfoAPI
from decouple import config

# API URL and key.
API_URL = config('API_URL')
API_KEY = config('API_KEY')


class TestDayGameInfoAPI(TestCase):
    def test_fetch_data(self):
        """
        Test whether game fetching works.

        """
        day_game_api = DayGameInfoAPI(API_URL, API_KEY)
        games = day_game_api.fetch_games(5, 25, 2019)
        # There should be 16 games.
        self.assertEqual(16, len(games))
        # Get specific game and test it.
        game = [game for game in games if game.home_team == 'Cubs'][0]
        self.assertEqual('2019_05_25_cinmlb_chnmlb_1', game.game_id)
