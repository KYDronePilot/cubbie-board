from PIL import Image
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time

# Default RST pins 25 and 23
# Default SPI devices 0 and 1

class LogoDisplay:
    def __init__(self, RST, SPI_DEVICE):
        # Key name of last displayed image, prevents unnecessary updates.
        self.key_name = ''
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
        # Initialize display.
        self.disp.begin()
    
    # Display the logo for a given team name (NL and AL logos included).
    def dispLogo(self, team_name):
        # Only update the display if key name is different than current.
        if self.key_name != team_name:
            self.key_name = team_name
            # Get the logo and display it.
            logo = Image.open('./logos/{0}.jpg'.format(team_name))
            self.disp.display(logo)