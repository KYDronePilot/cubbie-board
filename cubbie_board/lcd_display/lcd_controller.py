# For handling all operations on the two LCD displays.
from PIL import Image, ImageFont, ImageDraw

from lcd_display import LCDDisplay

FONT_DIR = 'font/'


# Thread to control LCD displays.
class LcdController:
    def __init__(self, home, away):
        """

        :type away: LCDDisplay
        :type home: LCDDisplay
        """
        # Home and away display objects.
        self.home = home
        self.away = away
        # Current images that are being displayed on each display.
        self.home_image = None
        self.away_image = None

    def __del__(self):
        # Dim displays.
        self.off()
        # Stop PWM threads.
        self.home.pwm.shut.set()
        self.away.pwm.shut.set()
        self.home.pwm.join()
        self.away.pwm.join()

    # Turn off the backlight for both displays.
    def off(self):
        # Dim displays.
        self.away.pwm.q.put((0, 0, False), block=False)
        self.home.pwm.q.put((0, 0, False), block=False)
        # Wait till dimmed.
        while self.away.pwm.current > 0 or self.home.pwm.current > 0:
            pass

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
                exec ("{0}_logo = self.renderWinner('{1}', {0}_logo)".format(val[0], val[1]))
        # Display the images.
        self.display_image('home', home_logo)
        self.display_image('away', away_logo)
        # Brighten screens if dim.
        self.home.pwm.q.put((100, 100, False), block=False)
        self.away.pwm.q.put((100, 100, False), block=False)
