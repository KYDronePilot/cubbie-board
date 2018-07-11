from os.path import isfile
from time import sleep

import pigpio

import daemon
import segment_display
from active_games import ActiveGames
from lcd_display.lcd_controller import LcdController
from lcd_display.lcd_display import LogoDisplay
from scoreboard import Scoreboard
from update_seg_disp import SegmentController

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
class CubbieBoardDaemon(daemon.Daemon):
    sb = None  # type: Scoreboard
    active_games = None  # type: ActiveGames
    lcd_ctl = None  # type: LcdController
    segment_ctl = None  # type: SegmentController

    # Define all vars here, but don't initialize any of them.
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        daemon.Daemon.__init__(self, pidfile, stdin=stdin, stdout=stdout, stderr=stderr)
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
        # For holding the game currently being displayed.
        self.game = None

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
        # Start segment controller thread.
        self.segment_ctl.start()
        # Signify that the displays are off.
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

    # For determining if the daemon should still be running.
    @staticmethod
    def running():
        # If daemon status file exists, return True, else False.
        return isfile(daemon.DAEMON_STATUS_DIR + 'running')

    # Special sleep function, checks daemon control var at 1 second intervals.
    def sleep(self, secs):
        """

        :type secs: int
        """
        # Use passed secs var as a counter.
        while secs > 0:
            # If daemon needs to stop, return here.
            if not self.running():
                return
            secs -= 1
            # Wait a sec...
            sleep(1)

    # Update the LCD displays.
    def updateLCD(self):
        # Extra kwargs to pass to display function.
        kwargs = dict()
        # If game is over or final, add winner as a kwarg for the display function.
        if self.sb.game_status == 'Game Over' or self.sb.game_status == 'Final':
            kwargs['winner'] = self.sb.getWinner()
        # Update the display.
        self.lcd_ctl.displayLogos(self.sb.home_team_name, self.sb.away_team_name, **kwargs)
        # Signify that the display should be on.
        self.displays_on = True

    # Main loop, manages everything.
    def run(self):
        # Run all initialization tasks.
        self.init()
        # Run till control var says to stop.
        while self.running():
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
            # There is a live game if the execution reaches here.
            # Get a game from the queue and see if that game is already being displayed.
            game = self.active_games.q.get()
            # If this is the first time through or a new game is to be displayed, reset this class's game object.
            if self.game is None or game.game_id != self.game.game_id:
                self.game = game
            # Update the scoreboard and get changes.
            changes = self.sb.update(game.game_id)
            # If a new game or status change, update the LCD displays.
            if 'new_game' in changes or 'status' in changes:
                self.updateLCD()
            # Update the segment displays.
            self.segment_ctl.q.put(changes, block=False)
            # Wait before refreshing or moving to the next game.
            self.sleep(10)
        # Shut down both controllers.
        self.segment_ctl.shut.set()
        del self.segment_ctl
        del self.lcd_ctl
