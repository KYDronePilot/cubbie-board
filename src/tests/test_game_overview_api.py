from unittest import TestCase

from decouple import config

from ..game_overview_api import GameOverviewAPI

# API URL and key.
API_URL = config('GAME_OVERVIEW_API_URL')
API_KEY = config('API_KEY')


class TestGameOverviewAPI(TestCase):
    def test_fetch_overviews(self):
        """
        Test API fetching.

        """
        # IDs to test with.
        ids = [
            '2019_05_24_cinmlb_chnmlb_1',
            '2019_05_24_miamlb_wasmlb_1'
        ]
        overview_api = GameOverviewAPI(API_URL, API_KEY)
        # Get overview for 2 games.
        overviews = overview_api.fetch_overviews(ids)
        # There should be 2.
        self.assertEqual(2, len(overviews))
        overviews.sort(key=lambda x: x.game_id)
        # Check IDs match.
        self.assertListEqual(ids, [game.game_id for game in overviews])
