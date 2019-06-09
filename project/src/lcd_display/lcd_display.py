"""
For modeling the LCD scoreboard displays.

"""

import os.path as path

import Adafruit_GPIO.SPI as SPI
import ST7735 as TFT
import pigpio
from PIL import Image, ImageFont, ImageDraw
from decouple import config
from typing import Tuple, ClassVar, Dict, Callable

from games.game_overview import GameOverview
from .backlight_controller import BacklightController


# Default RST pins 25 and 23
# Default SPI devices 0 and 1

class LCDDisplay(TFT.ST7735):
    """
    Represents one of the LCD scoreboard displays.

    Notes:
        Inherits from display controller class, fundamental representation of display.

    Attributes:
        _status_header_add_functions (Dict[str, Callable]): Functions for adding header status text
        _default_font (ImageFont.FreeTypeFont): Font used to draw on images
        _width (int): Display width
        _height (int): Display height
        backlight (BacklightController): Backlight controller for display

    """

    # Background colors.
    RED = (224, 13, 13)  # type: ClassVar[Tuple[int, int, int]]
    BLACK = (0, 0, 0)  # type: ClassVar[Tuple[int, int, int]]
    BLUE = (0, 53, 178)  # type: ClassVar[Tuple[int, int, int]]
    GRAY = (76, 76, 76)  # type: ClassVar[Tuple[int, int, int]]
    # Font colors.
    WHITE = (255, 255, 255)  # type: ClassVar[Tuple[int, int, int]]

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
        # Status header add functions for different statuses.
        self._status_header_add_functions = {
            GameOverview.WARM_UP_STATUS: self._add_warm_up_header,
            GameOverview.FINAL_STATUS: self._add_final_header,
            GameOverview.POSTPONED_STATUS: self._add_postponed_header
        }  # type: Dict[str, Callable]
        # Load the default font to be used.
        self._default_font = LCDDisplay._get_font('arial.ttf', 15)  # type: ImageFont.FreeTypeFont
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

    @staticmethod
    def _get_font(font_file, size):
        # type: (str, int) -> ImageFont.FreeTypeFont
        """
        Load font from a file.

        Args:
            font_file (str): File to load from
            size (int): Size of font

        Returns:
            ImageFont.FreeTypeFont: Font instance

        """
        return ImageFont.truetype(
            path.join(
                path.dirname(path.dirname(__file__)),
                config('FONT_DIR'),
                font_file
            ), size
        )

    @staticmethod
    def _draw_text_background(text, image, text_x, text_y, bg_x, bg_y, bg_w, bg_h, font, font_color, bg_color):
        """
        Draw text with background on an image.

        Args:
            text (str): Text to draw
            image (Image): Image to draw on
            text_x (int): X-coordinate of text
            text_y (int): Y-coordinate of text
            bg_x (int): X-coordinate of background
            bg_y (int): Y-coordinate of background
            bg_w (int): Width of background
            bg_h (int): Height of background
            font (ImageFont.FreeTypeFont): Font to draw with
            font_color (Tuple[int, int, int]): Color of font in RGB
            bg_color (Tuple[int, int, int]): Color of background in RGB

        Returns:
            Image: Image with text drawn on it

        """
        # Get draw instance.
        draw = ImageDraw.Draw(image)
        # Draw the background.
        draw.rectangle((bg_x, bg_y, bg_w, bg_h), fill=bg_color)
        # Draw the text.
        draw.text((text_x, text_y), text, fill=font_color, font=font)
        return image

    def _add_header_text(self, text, image, font_color, bg_color):
        # type: (str, Image, Tuple[int, int, int], Tuple[int, int, int]) -> Image
        """
        Add header text to an image.

        Adds text to the top of the image.

        Args:
            text (str): Text to add
            image (Image): Image to add header to
            font_color (Tuple[int, int, int]): Color of font
            bg_color (Tuple[int, int, int]): Color of background

        Returns:
            Image: Image with header

        """
        # Get dimensions of text with font.
        text_w, text_h = self._default_font.getsize(text)
        # Calculate text coordinates.
        text_x = (self._width - text_w) // 2
        text_y = 2
        # Draw the text and background.
        return self._draw_text_background(
            text,
            image,
            text_x,
            text_y,
            0,
            0,
            self._width,
            text_h + 4,
            self._default_font,
            font_color,
            bg_color
        )

    def _add_bottom_text(self, text, image):
        # type: (str, Image) -> Image
        """
        Add text to the bottom of an image.

        Args:
            text (str): The text to add
            image (Image): Image to draw on

        Returns:
            Image: Annotated image

        """
        # Get size of text.
        text_w, text_h = self._default_font.getsize(text)
        # Calculate text coordinates.
        text_x = 5
        text_y = self._height - 5 - text_h
        # Draw the text and background.
        return self._draw_text_background(
            text,
            image,
            text_x,
            text_y,
            0,
            text_y - 5,
            text_w + 10,
            text_y + text_h + 5,
            self._default_font,
            LCDDisplay.WHITE,
            LCDDisplay.GRAY
        )

    def add_winner_text(self, team, logo):
        # type: (str, Image) -> Image
        """
        Add text saying who won the game.

        Args:
            team (str): Name of team who won
            logo (Image): Logo of team who won

        Returns:
            Image: Team logo with winner text

        """
        # Text to add.
        win_label = team + ' won!'
        # Add text.
        return self._add_bottom_text(win_label, logo)

    def _add_final_header(self, image):
        # type: (Image) -> Image
        """
        Add final status header to an image.

        Args:
            image (Image): Image to add header to

        Returns:
            Image: Image with status header

        """
        return self._add_header_text('Final', image, LCDDisplay.WHITE, LCDDisplay.BLACK)

    def _add_warm_up_header(self, image):
        # type: (Image) -> Image
        """
        Add warm-up header to an image.

        Args:
            image (Image): Image to add header to

        Returns:
            Image: Image with status header

        """
        return self._add_header_text('Warm-Up', image, LCDDisplay.WHITE, LCDDisplay.BLUE)

    def _add_postponed_header(self, image):
        # type: (Image) -> Image
        """
        Add postponed status header to an image.

        Args:
            image (Image): Image to add header to

        Returns:
            Image: Image with status header

        """
        return self._add_header_text('Postponed', image, LCDDisplay.WHITE, LCDDisplay.RED)

    def add_status_header(self, status, image):
        # type: (str, Image) -> Image
        """
        Add status text to the top of the image.

        Args:
            status (str): Status of the game
            image (Image): Image to draw text on

        Returns:
            Image: Image with status text

        """
        # If no function for status, do nothing.
        if status not in self._status_header_add_functions:
            return image
        # Get function and call it.
        handler = self._status_header_add_functions[status]
        return handler(image)
