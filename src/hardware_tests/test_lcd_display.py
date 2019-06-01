from unittest import TestCase
from PIL import Image
from lcd_display import LCDDisplay
import pigpio


class TestLCDDisplay(TestCase):
    def setUp(self):
        # type: () -> None
        """
        Set up the right display.

        """
        self.gpio = pigpio.pi()
        self.display = LCDDisplay(
            25,
            0,
            0,
            12,
            24,
            4000000,
            self.gpio,
            128,
            128
        )
        # Test logos.
        self.cubs_logo = Image.open('img/Cubs.jpg')
        self.cardinals_logo = Image.open('img/Cardinals.jpg')

    def test_display_image(self):
        """
        Try displaying a test Cubs logo.

        """
        self.display.display_image(self.cubs_logo)

    def test__add_text(self):
        self.fail()

    def test_add_winner_text(self):
        self.fail()
