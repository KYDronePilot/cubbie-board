# For handling all operations on the two LCD displays.
from PIL import Image, ImageFont, ImageDraw
from lcd_display import LogoDisplay

FONT_DIR = 'font/'

# Thread to control LCD displays.
class LcdController():
    def __init__(self, home, away):
        """

        :type away: LogoDisplay
        :type home: LogoDisplay
        """
        # Home and away display objects.
        self.home = home
        self.away = away
        # Current images that are being displayed on each display.
        self.home_image = None
        self.away_image = None

    def __del__(self):
        print("LcdController del triggered")
        # Dim displays.
        self.away.pwm.q.put((0, 0, False), block=False)
        self.home.pwm.q.put((0, 0, False), block=False)
        # Wait till dimmed.
        while self.away.pwm.current > 0 or self.home.pwm.current > 0:
            pass
        # Stop PWM threads.
        self.home.pwm.shut.set()
        self.away.pwm.shut.set()
        self.home.pwm.join()
        self.away.pwm.join()

    # For displaying a team logo.
    def displayLogo(self, home_away, team_name):
        # Display image by specifying the path where logos are and inserting the team name.
        self.displayImage(home_away, 'logos/{}'.format(team_name))

    # Display an image by its file name.
    def displayImage(self, home_away, filename):
        # Open the specified file.
        im = Image.open('img/{}.jpg'.format(filename))
        # Display it on the specified display.
        getattr(self, home_away).displayImage(image=im)

    # Show who won the game.
    def displayWinner(self, home_away, team_name):
        # Get a font object.
        font = ImageFont.truetype(FONT_DIR + 'arial.ttf', 15)
        # Text to be written.
        text = '{} won!'.format(team_name)
        # Get size of text from font object.
        w, h = font.getsize(text)
        # Where the text will be drawn.
        x = 5
        y = 128 - h - 5
        # Get image from cache.
        image = getattr(self, home_away).image_cache
        # Get draw object.
        draw = ImageDraw.Draw(image)
        # Draw a rectangular background to make the text stand out.
        draw.rectangle((x - 5, y - 5, w + x + 5, h + y + 5), fill='black')
        # Draw the text inside the box.
        draw.text((x, y), text, fill=(180, 180, 180), font=font)
        # Display the image.
        getattr(self, home_away).displayImage(image=image)


    # Initialize display for start of game.
    def init(self, home, away):
        # display the home and away logos.
        self.displayLogo('home', home)
        self.displayLogo('away', away)
        # Raise the brightness on both displays.
        self.home.pwm.q.put((100, 100, False), block=False)
        self.away.pwm.q.put((100, 100, False), block=False)
