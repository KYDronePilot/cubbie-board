"""
For modeling the LCD scoreboard displays.

"""

import Adafruit_GPIO.SPI as SPI
import ST7735 as TFT

from cubbie_board.lcd_display.pwm_controller import PWMController
from typing import List


# Default RST pins 25 and 23
# Default SPI devices 0 and 1

class LCDDisplay:
    """
    Represents one of the LCD scoreboard displays.

    Attributes:
        width (int): Display width
        height (int): Display height

    """

    def __init__(self, reset_pin, spi_device, pwm_pin, gpio):
        # type: (int, int, int, pigpio) -> None
        """
        Basic display constructor.

        Args:
            reset_pin (int): Reset pin for display
            spi_device (int): SPI Device index
            pwm_pin (int): Display PWM pin
            gpio (pigpio): GPIO instance for controlling PWM

        """
        # Dimensions of Adafruit ST7735r display.
        self.WIDTH = 128
        self.HEIGHT = 128
        # SPI clock speed.
        self.SPEED_HZ = 4000000
        # Data/Command pin.
        self.DC = 24
        # Reset pin for display.
        self.RST = reset_pin
        # SPI port.
        self.SPI_PORT = 0
        # SPI Device.
        self.SPI_DEVICE = spi_device
        # New object for diplay.
        self.disp = TFT.ST7735(
            self.DC,
            rst=self.RST,
            spi=SPI.SpiDev(
                self.SPI_PORT,
                self.SPI_DEVICE,
                max_speed_hz=self.SPEED_HZ
            )
        )
        # Holds the last image displayed.
        self.image_cache = None
        # Start PWM thread.
        self.pwm = PWMController(pwm_pin, gpio)
        self.pwm.start()
        # Initialize display.
        self.disp.begin()

    # Display a cached image if none specified or a specified image.
    def display_image(self, image=None):
        # If no image was specified, use the cache.
        if image is None:
            image = self.image_cache
        # Fail-safe, if no image was in the cache either.
        if image is None:
            print('No image to display!')
            return
        # Cache the image.
        self.image_cache = image
        # Display the image.
        self.disp.display(image)
