# For handling all operations on the two LCD displays.
from PIL import Image
from lcd_display import LogoDisplay


# Thread to control LCD displays.
class LcdController(object):
    def __init__(self, home, away):
        """

        :type away: LogoDisplay
        :type home: LogoDisplay
        """
        # Home and away display objects.
        self.home = home
        self.away = away

    def __del__(self):
        print("LcdController del triggered")
        # Dim displays.
        self.away.pwm.q.put((0, 0, False), block=False)
        self.home.pwm.q.put((0, 0, False), block=False)
        # Wait till dimmed.
        while self.away.pwm.current > 0 and self.home.pwm.current > 0:
            pass
        # Stop PWM threads.
        self.home.pwm.shut.set()
        self.away.pwm.shut.set()
        self.home.pwm.join()
        self.away.pwm.join()

    # For displaying a team logo.
    def displayLogo(self, home_away, team_name):
        # Get the image file.
        im = Image.open('logos/{}.jpg'.format(team_name))
        # Get the proper display object and display the image.
        getattr(self, home_away).displayImage(im)

    # Initialize display for start of game.
    def init(self, home, away):
        # display the home and away logos.
        self.displayLogo('home', home)
        self.displayLogo('away', away)
        # Raise the brightness on both displays.
        self.home.pwm.q.put((100, 100, False), block=False)
        self.away.pwm.q.put((100, 100, False), block=False)
