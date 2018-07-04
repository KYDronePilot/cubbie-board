from lcd_display.lcd_display import LogoDisplay
from scoreboard import Scoreboard
from sys import argv
from time import sleep
import segment_display
from update_seg_disp import SegmentController
import pigpio
from lcd_display.lcd_controller import LcdController
from daemon import Daemon
from active_games import ActiveGames

# I2C addresses for the controllers of the segment displays.
HOME_SEG_ADDR = 0x21
AWAY_SEG_ADDR = 0x20
INNING_SEG_ADDR = 0x24
# GPIO pins for controlling which digit on the dual digit displays is on.
# This is necessary for running two digits at the same time.
LEFT_DIGIT_TRANSISTOR = 17
RIGHT_DIGIT_TRANSISTOR = 4
# Preferred team that supersedes all others when live.
PREFERRED_TEAM = 'Cubs'


# Main daemon that drives everything.
class CubbieBoardDaemon(Daemon):
    sb = None  # type: Scoreboard
    active_games = None  # type: ActiveGames
    lcd_ctl = None  # type: LcdController
    segment_ctl = None  # type: SegmentController

    # Define all vars here, but don't initialize any of them.
    def __init__(self):
        Daemon.__init__(self)
        # Pigpio daemon control object.
        self.gpio = None
        # Home and away LCD objects.
        self.home_lcd = None
        self.away_lcd = None
        # LCD controller object.
        self.lcd_ctl = None
        # 7-segment display objects.
        self.home_segment = None
        self.away_segment = None
        self.inning_segment = None
        # 7-segment display updater (controller)
        self.segment_ctl = None
        # For getting a list of active games.
        self.active_games = None
        # For keeping track of whether the displays are on or off.
        self.displays_on = False
        # Scoreboard for getting the latest game info.
        self.sb = None

    # Initialize all display hardware and related controllers.
    def init(self):
        # Initialize pigpio object for PWM.
        self.gpio = pigpio.pi()
        # Initialize both LCD displays.
        self.home_lcd = LogoDisplay(25, 0, 12, self.gpio)
        self.away_lcd = LogoDisplay(23, 1, 13, self.gpio)
        # Give the LCD display objects to their controller.
        self.lcd_ctl = LcdController(self.home_lcd, self.away_lcd)
        # Create segment display objects for the home, away, and inning 7-segment displays.
        self.home_segment = segment_display.MCP23008(1, HOME_SEG_ADDR)
        self.away_segment = segment_display.MCP23008(1, AWAY_SEG_ADDR)
        self.inning_segment = segment_display.MCP23008(1, INNING_SEG_ADDR)
        # Give segment display objects to their controllers.
        self.segment_ctl = SegmentController(
            self.home_segment,
            self.away_segment,
            self.inning_segment,
            left_dig_tran=LEFT_DIGIT_TRANSISTOR,
            right_dig_tran=RIGHT_DIGIT_TRANSISTOR
        )
        # Signify that the displays are of.
        self.displays_on = False
        # Holds a queue with active games that can be refilled with the refill method.
        self.active_games = ActiveGames(PREFERRED_TEAM)
        # Initialize scoreboard object, cannot be used till game_id specified.
        self.sb = Scoreboard()

    # Shut off the displays.
    def off(self):
        # Turn off the 7-segment displays.
        self.segment_ctl.q.put({'off': None}, block=False)
        # Turn off the LCD displays.
        self.lcd_ctl.off()
        # Set the display status var to off.
        self.displays_on = False

    # Special sleep function, checks daemon control var at 1 second intervals.
    def sleep(self, secs):
        """

        :type secs: int
        """
        # Use passed secs var as a counter.
        while secs > 0:
            # If daemon needs to stop, return here.
            if self.shut:
                return
            secs -= 1
            # Wait a sec...
            sleep(1)

    # Main loop, manages everything.
    def run(self):
        # Run all initialization tasks.
        self.init()
        # Run till control var says to stop.
        while not self.shut:
            # Check if there are any live games.
            if self.active_games.q.empty():
                # If none in queue, try to refill.
                self.active_games.refill()
                # If there still aren't any live games, wait 10 minutes and check again.
                if self.active_games.q.empty():
                    # Shut off the displays if on.
                    if self.displays_on:
                        self.off()
                    # Wait 10 minutes before checking again for games.
                    self.sleep(600)
                    continue
            # Else, there are active games.
            else:
                # Pop a game off the queue.
                game = self.active_games.q.get()
                # Get a live scoreboard for that game.
                self.sb.game_id = game.game_id
                changes = self.sb.update()
                # Send changes to the segment displays controller.
                self.segment_ctl.q.put(changes, block=False)
                # Display the team logos and brighten the screens if dim.
                self.lcd_ctl.showTeams(sb.home_team_name, sb.away_team_name)
                # Wait before checking moving to the next game.
                self.sleep(10)
        # Close SegmentUpdater object.
        self.segment_ctl.shut.set()
        del self.segment_ctl
        # Shut down LCD displays, in other words, dim screens and stop PWM threads.
        del self.lcd_ctl


exit()

# Get the game ID as the one and only argument accepted by this script.
game_id = argv[1]

# Get a scoreboard object, and initial important values stored in the scoreboard object; the team names.
sb = Scoreboard(game_id)
sb.initialize()

# Object that handles updating the segment displays.
segment_ctl = SegmentController(home_segment, away_segment, inning_segment, 17, 4, q)
# Initialize LCD displays.
lcd_ctl.init(sb.home_team_name, sb.away_team_name)
# Start the segment updater thread.
segment_ctl.start()


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
segment_ctl.shut.set()
del segment_ctl
# Shut down LCD displays, in other words, dim screens and stop PWM threads.
del lcd_ctl
