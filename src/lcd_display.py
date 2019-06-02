"""
For modeling the LCD scoreboard displays.

"""

import os.path as path

import Adafruit_GPIO.SPI as SPI
import ST7735 as TFT
import pigpio
from PIL import Image, ImageFont, ImageDraw
from decouple import config

from backlight_controller import BacklightController


# Default RST pins 25 and 23
# Default SPI devices 0 and 1

class LCDDisplay(TFT.ST7735):
    """
    Represents one of the LCD scoreboard displays.

    Notes:
        Inherits from display controller class, fundamental representation of display.

    Attributes:
        width (int): Display width
        height (int): Display height

    """

    def __init__(self, reset_pin, spi_device, spi_port, pwm_pin, dc_pin, clock_speed, gpio, width, height):
        # type: (int, int, int, int, int, int, pigpio.pi, int, int) -> None
        """
        Setup display controller.

        Args:
            reset_pin (int): Reset pin for display
            spi_device (int): SPI Device index
            spi_port (int): SPI port number
            pwm_pin (int): Display backlight PWM pin
            dc_pin (int): Data/Command pin
            clock_speed (int): SPI clock speed
            gpio (pigpio): GPIO instance for controlling PWM
            width (int): Width of display (pixels)
            height (int): Height of display (pixels)

        """
        # Construct super.
        TFT.ST7735.__init__(
            self,
            dc_pin,
            rst=reset_pin,
            spi=SPI.SpiDev(
                spi_port,
                spi_device,
                max_speed_hz=clock_speed
            )
        )
        # Actual dimensions of display.
        self._width = width  # type: int
        self._height = height  # type: int
        self.backlight = BacklightController(pwm_pin, gpio)  # type: BacklightController
        # Start backlight thread.
        self.backlight.start()
        # Initialize display.
        self.begin()

    def exit(self):
        # type: () -> None
        """
        Prepare display for script exit.

        """
        # Stop backlight thread.
        self.backlight.stop()

    def display_image(self, image):
        # type: (Image) -> None
        """
        Wrapper for displaying images.

        Args:
            image (Image): The image to display

        """
        # Display the image.
        self.display(image)

    def _add_text(self, text, image, font='arial.ttf'):
        # type: (str, Image, str) -> Image
        """
        Add text to an image.

        Args:
            text (str): The text to add
            image (Image): Image to draw on
            font (str): Name of font file

        Returns:
            Image: Annotated image

        """
        # Get font.
        font = ImageFont.truetype(
            path.join(path.join(path.dirname(path.dirname(__file__))),
                      config('FONT_DIR'),
                      font
                      ),
            15
        )
        # Get size of text.
        w, h = font.getsize(text)
        # Where the text will be drawn.
        x = 5
        y = self._height - h - 5
        draw = ImageDraw.Draw(image)
        # Draw a rectangular background to make text stand out.
        draw.rectangle((x - 5, y - 5, w + x + 5, h + y + 5), fill=(76, 76, 76))
        # Draw text on rectangle.
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        return image

    def add_winner_text(self, team, logo):
        # type: (str, Image) -> Image
        """
        Add text of who won the game

        Args:
            team (str): Name of team who won
            logo (Image): Logo of team who won

        Returns:
            Image: Team logo with winner text

        """
        # Text to add.
        win_label = team + ' won!'
        # Add text.
        return self._add_text(win_label, logo)
