from unittest import TestCase

from ..game_overview import GameOverview


class TestGameOverview(TestCase):
    def test__process_time(self):
        """
        Test how times are processed.

        """
        # Test actual time from a game.
        date = GameOverview._process_time('2019/05/24 2:20', 'PM')
        self.assertEqual(2019, date.year)
        self.assertEqual(5, date.month)
        self.assertEqual(24, date.day)
        self.assertEqual(14, date.hour)
        self.assertEqual(20, date.minute)
        # Try AM.
        date = GameOverview._process_time('2019/05/24 2:20', 'AM')
        self.assertEqual(2, date.hour)
        # Try lowercase.
        date = GameOverview._process_time('2019/05/24 2:20', 'pm')
        self.assertEqual(14, date.hour)
        # Try non-zero padded minutes.
        date = GameOverview._process_time('2019/05/24 2:6', 'pm')
        self.assertEqual(6, date.minute)
        # Try zero padded minutes.
        date = GameOverview._process_time('2019/05/24 2:08', 'pm')
        self.assertEqual(8, date.minute)
        # Try zero padded hours.
        date = GameOverview._process_time('2019/05/24 02:08', 'pm')
        self.assertEqual(14, date.hour)
