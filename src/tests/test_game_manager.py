from datetime import date
from unittest import TestCase

from ..game_manager import GameManager


class TestGameManager(TestCase):
    def setUp(self):
        # type: () -> None
        """
        Set up new manager before each test.

        """
        self.manager = GameManager(
            date(2019, 5, 25),
            'Cubs'
        )

    def test_construction(self):
        # type: () -> None
        """
        Test construction of the object.

        """
        # There should be 16 games.
        self.assertEqual(16, len(self.manager.games))
        self.assertEqual(16, len(self.manager.overviews))
        # Check that an ID exist.
        self.assertTrue('2019_05_25_bosmlb_houmlb_1' in [game.game_id for game in self.manager.games])
        self.assertTrue('2019_05_25_bosmlb_houmlb_1' in [game.game_id for game in self.manager.overviews])
        # Check attributes.
        self.assertEqual(date(2019, 5, 25), self.manager.current_date)
        self.assertEqual('Cubs', self.manager.preferred_team)
        # Game index should be default.
        self.assertEqual(-1, self.manager.current_game_index)

    def test__get_team_overview_i(self):
        # Get index of Cubs game.
        cubs_i = self.manager._get_team_overview_i('Cubs')
        # Verify cubs are in game.
        self.assertTrue(self.manager.overviews[cubs_i].is_playing('Cubs'))
        # Try a team that doesn't exist.
        random_i = self.manager._get_team_overview_i('Some Team')
        # Should be invalid.
        self.assertEqual(-1, random_i)

    def test_refresh_overviews(self):
        # Set Cubs game as active.
        cubs_i = self.manager._get_team_overview_i('Cubs')
        self.manager.overviews[cubs_i].status = self.manager.overviews[cubs_i].IN_PROGRESS_STATUS
        # Change the score of another game.
        angels_i = self.manager._get_team_overview_i('Angels')
        self.manager.overviews[angels_i].home_team_runs = -1
        # Refresh overviews.
        self.manager.refresh_overviews()
        # Cubs should be updated.
        self.assertTrue(self.manager.overviews[cubs_i].is_final())
        # Angels should not.
        self.assertEqual(-1, self.manager.overviews[angels_i].home_team_runs)
        # Change the Cubs score.
        self.manager.overviews[cubs_i].home_team_runs = -1
        # Refresh again.
        self.manager.refresh_overviews()
        # Angels should change, Cubs should not.
        self.assertNotEqual(-1, self.manager.overviews[angels_i].home_team_runs)
        self.assertEqual(-1, self.manager.overviews[cubs_i].home_team_runs)
