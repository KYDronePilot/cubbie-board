from datetime import date
from unittest import TestCase

from games.game_manager import GameManager


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

    def test__update_overviews(self):
        """
        Test the overview update process.

        """
        # Set Cubs game as active.
        cubs_i = self.manager._get_team_overview_i('Cubs')
        self.manager.overviews[cubs_i].status = self.manager.overviews[cubs_i].IN_PROGRESS_STATUS
        # Change the score and status of another game.
        angels_i = self.manager._get_team_overview_i('Angels')
        self.manager.overviews[angels_i].home_team_runs = -1
        self.manager.overviews[angels_i].status = self.manager.overviews[angels_i].IN_PROGRESS_STATUS
        # Update the overviews.
        pref_team_i = self.manager._update_overviews()
        # Cubs should be updated and the preferred, active game.
        self.assertTrue(self.manager.overviews[cubs_i].is_final())
        self.assertEqual(cubs_i, pref_team_i)
        # Angels should not.
        self.assertEqual(-1, self.manager.overviews[angels_i].home_team_runs)
        # Change the Cubs score.
        self.manager.overviews[cubs_i].home_team_runs = -1
        # Update again.
        pref_team_i = self.manager._update_overviews()
        # Angels should change, Cubs should not.
        self.assertNotEqual(-1, self.manager.overviews[angels_i].home_team_runs)
        self.assertEqual(-1, self.manager.overviews[cubs_i].home_team_runs)
        # There should be no preferred, active team.
        self.assertEqual(-1, pref_team_i)

    def test_refill_queue(self):
        """
        Test the process of refilling the game queue.

        """
        # All games should be final and thus added.
        self.manager._refill_queue()
        cnt = 0
        while not self.manager.overview_queue.empty():
            self.assertTrue(self.manager.overview_queue.get().is_final())
            cnt += 1
        # Should be 16 games.
        self.assertEqual(16, cnt)
        # Set Cubs game as active.
        cubs_i = self.manager._get_team_overview_i('Cubs')
        self.manager.overviews[cubs_i].status = self.manager.overviews[cubs_i].IN_PROGRESS_STATUS
        # Should only refill that game.
        self.manager._refill_queue(pref_team_i=cubs_i)
        cnt = 0
        while not self.manager.overview_queue.empty():
            self.assertTrue(self.manager.overview_queue.get().is_active())
            cnt += 1
        self.assertEqual(1, cnt)

    # def test_refresh_overviews(self):
    #     # Change the score of the Angels game and make active.
    #     angels_i = self.manager._get_team_overview_i('Angels')
    #     self.manager.overviews[angels_i].home_team_runs = -1
    #     self.manager.overviews[angels_i].status = self.manager.overviews[angels_i].IN_PROGRESS_STATUS
    #     # Refresh
    #     self.manager.refresh_overviews()
    #     # Score should be updated.
    #     self.assertNotEqual(-1, self.manager.overviews[angels_i].home_team_runs)
    #     # Queue should have 16 items.
    #     cnt = 0
    #     while not self.manager.overview_queue.empty():
    #         self.manager.overview_queue.get()
    #         cnt += 1
    #     self.assertEqual(16, cnt)

    # def test_get_next_game(self):
    #     """
    #     Test the retrieval of a next game to display.
    #
    #     """
    #     # Queue should get refilled.
    #     game = self.manager.get_next_game()
    #     # Game should be final.
    #     self.assertTrue(game.is_final())
    #     # Queue should not be empty.
    #     self.assertFalse(self.manager.overview_queue.empty())
    #     # Remove remaining.
    #     cnt = 1
    #     while True:
    #         next_game = self.manager.get_next_game()
    #         if game.game_id == next_game.game_id:
    #             break
    #         else:
    #             cnt += 1
    #     # Should be 16.
    #     self.assertEqual(16, cnt)
