from lcd_display.lcd_display import LogoDisplay
from scoreboard import Scoreboard
from sys import argv
from time import sleep
import segment_display
from update_seg_disp import SegmentUpdater
from Queue import Queue
import pigpio
from lcd_display.lcd_controller import LcdController
from daemon import Daemon


# Main daemon that drives everything.
class CubbieBoardDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(self)
        # For pigpio daemon control object.
        self.gpio = None
        # All variables that will be needed in this class.
        self.home_lcd = None

    # Actions to be performed when the daemon has been started or restarted.
    def initBoot(self):
        # Initialize pigpio object for PWM.
        self.gpio = pigpio.pi()

    # Initialize all display hardware and related controllers.
    # To be executed when a game is starting.
    def init(self):
        # Initialize both LCD displays.
        self.home_lcd = LogoDisplay(25, 0, 12, gpio)
        away_lcd = LogoDisplay(23, 1, 13, gpio)
        # Give the LCD display objects to their controller.
        lcd_ctl = LcdController(home_lcd, away_lcd)
        # Create segment display objects for the home, away, and inning displays.
        home_segment = segment_display.MCP23008(1, 0x21)
        away_segment = segment_display.MCP23008(1, 0x20)
        inning_segment = segment_display.MCP23008(1, 0x24)



# Get the game ID as the one and only argument accepted by this script.
game_id = argv[1]

# Get a scoreboard object, and initial important values stored in the scoreboard object; the team names.
sb = Scoreboard(game_id)
sb.initialize()



# Queue to pass score and inning changes to the segment updater class.
q = Queue(maxsize=2)
# Object that handles updating the segment displays.
segment_updater = SegmentUpdater(home_segment, away_segment, inning_segment, 17, 4, q)
# Initialize LCD displays.
lcd_ctl.init(sb.home_team_name, sb.away_team_name)
# Start the segment updater thread.
segment_updater.start()







# Main loop.
def main():
    # Run loop which updates the scoreboard until game ends.
    while sb.game_status == running_status:
        # Update the scoreboard and get the changes in a dict.
        changes = sb.updateLive()
        # If there are changes, pass them to the segment display updater queue.
        if changes != {}:
            q.put(changes, True)
        # Wait 10 seconds before scanning again.
        sleep(10)
    # TODO add other post-game operations, like displaying a Cubs 'W' logo when the Cubs win.


# TODO configure for when game gets delayed.
try:
    main()
# Stop main when there is a keyboard interruption.
except:
    print("Exception received")

lcd_ctl.displayWinner('home', 'Cubs')
sleep(10)

# Close SegmentUpdater object.
segment_updater.shut.set()
del segment_updater
# Shut down LCD displays, in other words, dim screens and stop PWM threads.
del lcd_ctl
