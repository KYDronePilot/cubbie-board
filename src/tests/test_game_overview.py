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

    def test_is_active(self):
        """
        Test if it can determine whether a game is active.

        """
        # Should be active.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'In Progress',
            10,
            'Top',
            3,
            3,
            'Cardinals',
            'Braves',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertTrue(info.is_active())
        # Should be false.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'Final',
            10,
            'Top',
            3,
            3,
            'Cardinals',
            'Braves',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertFalse(info.is_active())

    def test_is_final(self):
        """
        Test if it can determine whether a game is over.

        """
        # Should be final.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'Final',
            10,
            'Top',
            3,
            3,
            'Cardinals',
            'Braves',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertTrue(info.is_final())
        # Should be false.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'In Progress',
            10,
            'Top',
            3,
            3,
            'Cardinals',
            'Braves',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertFalse(info.is_final())

    def test_is_pre_game(self):
        """
        Test if it can determine whether a game is in warm-up.

        """
        # Should be warm-up.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'Warmup',
            10,
            'Top',
            3,
            3,
            'Cardinals',
            'Braves',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertTrue(info.is_warm_up())
        # Should be false.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'In Progress',
            10,
            'Top',
            3,
            3,
            'Cardinals',
            'Braves',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertFalse(info.is_warm_up())

    def test_is_playing(self):
        """
        Verify that the method can check if a specific team is playing.

        """
        # Cubs are playing.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'In Progress',
            10,
            'Top',
            3,
            3,
            'Cubs',
            'Indians',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertTrue(info.is_playing('Cubs'))
        # Cubs are not playing.
        info = GameOverview(
            '2019_05_26_atlmlb_slnmlb_1',
            'In Progress',
            10,
            'Top',
            3,
            3,
            'Rays',
            'Indians',
            '2019/05/26 7:05',
            'PM'
        )
        self.assertFalse(info.is_playing('Cubs'))
