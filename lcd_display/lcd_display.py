from PIL import Image
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time
from pwm_controller import PWMController


# Default RST pins 25 and 23
# Default SPI devices 0 and 1

class LogoDisplay:
    def __init__(self, RST, SPI_DEVICE, pwm_pin, gpio):
        # Dimensions of Adafruit ST7735r display.
        self.WIDTH = 128
        self.HEIGHT = 128
        # SPI clock speed.
        self.SPEED_HZ = 4000000
        # Data/Command pin.
        self.DC = 24
        # Reset pin for display.
        self.RST = RST
        # SPI port.
        self.SPI_PORT = 0
        # SPI Device.
        self.SPI_DEVICE = SPI_DEVICE
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
    def displayImage(self, image=None):
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
