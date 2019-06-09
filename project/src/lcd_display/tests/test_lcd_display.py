from unittest import TestCase

import pigpio
from PIL import Image

from lcd_display.lcd_display import LCDDisplay


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
        """
        Try adding text to an image and displaying it.

        """
        image = self.display._add_bottom_text('Testing is awesome!', self.cubs_logo)
        self.display.display_image(image)

    def test_add_winner_text(self):
        """
        Try added text for the team that won and display it.

        """
        image = self.display.add_winner_text('Cubs', self.cubs_logo)
        self.display.display_image(image)
