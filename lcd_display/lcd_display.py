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
        # Start PWM thread.
        self.pwm = PWMController(12, gpio)
        self.pwm.start()
        # Initialize display.
        self.disp.begin()

    def __exit__(self, ext_type, exc_value, traceback):
        print("LogoDisplay exit triggered")
        # Send stop signal to PWM thread and wait till it ends.
        self.pwm.shut.set()
        self.pwm.join()

    def __del__(self):
        print("LogoDisplay del triggered")

    # Display a given image.
    def displayImage(self, image):
        self.disp.display(image)
