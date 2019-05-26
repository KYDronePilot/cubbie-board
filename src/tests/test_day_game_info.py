from unittest import TestCase

from ..day_game_info import DayGameInfo


class TestDayGameInfo(TestCase):
    def test_construction(self):
        """
        Test construction of the object.

        """
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'IN_PROGRESS',
            'Indians',
            'Rays'
        )
        # Check attributes.
        self.assertEqual('2019_05_25_tbamlb_clemlb_1', info.game_id)
        self.assertEqual(2019, info.date.year)
        self.assertEqual(5, info.date.month)
        self.assertEqual(25, info.date.day)
        self.assertEqual(16, info.date.hour)
        self.assertEqual(10, info.date.minute)
        self.assertEqual(0, info.date.second)
        self.assertEqual('04:10 pm', info.game_start_time)
        self.assertEqual('IN_PROGRESS', info.game_status)
        self.assertEqual('Indians', info.home_team)
        self.assertEqual('Rays', info.away_team)

    def test_is_active(self):
        """
        Test if it can determine whether a game is active.

        """
        # Should be active.
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'IN_PROGRESS',
            'Indians',
            'Rays'
        )
        self.assertTrue(info.is_active())
        # Should be false.
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'FINAL',
            'Indians',
            'Rays'
        )
        self.assertFalse(info.is_active())

    def test_is_final(self):
        """
        Test if it can determine whether a game is over.

        """
        # Should be final.
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'FINAL',
            'Indians',
            'Rays'
        )
        self.assertTrue(info.is_final())
        # Should be false.
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'PRE_GAME',
            'Indians',
            'Rays'
        )
        self.assertFalse(info.is_final())

    def test_is_pre_game(self):
        """
        Test if it can determine whether a game is in pre-game.

        """
        # Should be pre-game.
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'PRE_GAME',
            'Indians',
            'Rays'
        )
        self.assertTrue(info.is_pre_game())
        # Should be false.
        info = DayGameInfo(
            '2019_05_25_tbamlb_clemlb_1',
            '2019-05-25T16:10:00',
            '04:10 pm',
            'FINAL',
            'Indians',
            'Rays'
        )
        self.assertFalse(info.is_pre_game())
