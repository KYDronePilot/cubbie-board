# For handling all operations on the two LCD displays.
from PIL import Image, ImageFont, ImageDraw

from src.lcd_display import LCDDisplay
from typing import List, Dict
from decouple import config
import pigpio
import os.path
import os

FONT_DIR = 'font/'


# Thread to control LCD displays.
class LcdController:
    """
    LCD display controller.

    Attributes:
        home_display (LCDDisplay): Home LCD display
        away_display (LCDDisplay): Away LCD display
        logos (Dict[str, Image]): Team name -> team logo for all logos

    """

    def __init__(self):
        # type: () -> None
        """
        Initialize LCD displays.

        """
        # Configure the home and away LCD displays.
        self.home_display = LCDDisplay(
            config('HOME_LCD_RESET_PIN'),
            config('HOME_LCD_SPI_DEVICE'),
            config('LCD_SPI_PORT'),
            config('HOME_LCD_PWM_PIN'),
            config('LCD_DC_PIN'),
            config('LCD_SPI_CLOCK_SPEED'),
            pigpio.pi(),
            config('LCD_WIDTH'),
            config('LCD_HEIGHT')
        )  # type: LCDDisplay
        self.away_display = LCDDisplay(
            config('AWAY_LCD_RESET_PIN'),
            config('AWAY_LCD_SPI_DEVICE'),
            config('LCD_SPI_PORT'),
            config('AWAY_LCD_PWM_PIN'),
            config('LCD_DC_PIN'),
            config('LCD_SPI_CLOCK_SPEED'),
            pigpio.pi(),
            config('LCD_WIDTH'),
            config('LCD_HEIGHT')
        )  # type: LCDDisplay
        self.logos = {}  # type: Dict[str, Image]

    def exit(self):
        # type: () -> None
        """
        Prepare displays for script exit.

        """
        # Exit the displays.
        self.home_display.exit()
        self.away_display.exit()

    @staticmethod
    def _get_images(path):
        # type: (str) -> Dict[str, Image]
        """
        Get all jpg images in a directory.

        Args:
            path (str): Directory to look in

        Returns:
            Dict[str, Image]: Images in directory as image name -> image object

        """
        return {item.split('.jpg')[0]: Image.open(item) for item in os.listdir(path) if item.endswith('.jpg')}

    def load_logos(self):
        # type: () -> None
        """
        Load the team logos images into memory.

        """
        # Format logo path.
        logo_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), config('LOGO_DIR')))
        # Get and set all images to attribute.
        self.logos = self._get_images(logo_path)

    # Get an image object from file.
    def open_image(self, filename, logo=False):
        # Extra path to team logos.
        logo_path = str()
        # If the image is a logo, set the path.
        if logo:
            logo_path = 'logos/'
        # Open the specified file and return it.
        return Image.open('img/{0}{1}.jpg'.format(logo_path, filename))

    # Display an image object.
    def display_image(self, home_away, image):
        # Display it on the specified display.
        getattr(self, home_away).display_image(image=image)

    # Render an image to be displayed that shows who won on the winner's LCD display.
    def render_winner_label(self, team_name, image):
        # If the team that won is the Cubs, come on, there's gotta be a 'W'.
        if team_name == 'Cubs':
            return self.open_image('cubs_w_flag')
        # Get a font object.
        font = ImageFont.truetype(FONT_DIR + 'arial.ttf', 15)
        # Text to be written.
        text = '{} won!'.format(team_name)
        # Get size of text from font object.
        w, h = font.getsize(text)
        # Where the text will be drawn.
        x = 5
        y = 128 - h - 5
        # Get draw object.
        draw = ImageDraw.Draw(image)
        # Draw a rectangular background to make the text stand out.
        draw.rectangle((x - 5, y - 5, w + x + 5, h + y + 5), fill=(76, 76, 76))
        # Draw the text inside the box.
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        # Return image.
        return image

    # Show team logos, overlaying any necessary information based on extra kwargs.
    def display_team_logos(self, home_team, away_team, **kwargs):
        # Get team logos.
        home_logo = self.open_image(home_team, logo=True)
        away_logo = self.open_image(away_team, logo=True)
        # Perform operations based on kwargs.
        for key, val in kwargs.items():
            # If a winner is specified, alter their team logo accordingly.
            if key == 'winner':
                # Update the logo of the winning team.
                exec ("{0}_logo = self.render_winner_label('{1}', {0}_logo)".format(val[0], val[1]))
        # Display the images.
        self.display_image('home', home_logo)
        self.display_image('away', away_logo)
        # Brighten screens if dim.
        self.home.backlight.q.put((100, 100, False), block=False)
        self.away.backlight.q.put((100, 100, False), block=False)
