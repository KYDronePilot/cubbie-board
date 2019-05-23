import signal
from time import sleep
from urllib2 import URLError
from py_daemon.py_daemon import Daemon
from lxml.etree import XMLSyntaxError

import pigpio

from cubbie_board.core.active_games import ActiveGames
from cubbie_board.core.scoreboard import Scoreboard
from cubbie_board.lcd_display.lcd_controller import LcdController
from cubbie_board.lcd_display.lcd_display import LCDDisplay
from cubbie_board.segment_display import segment_display
from cubbie_board.segment_display.segment_controller import SegmentController

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
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        Daemon.__init__(self, pidfile, stdin=stdin, stdout=stdout, stderr=stderr)
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
        # Set catch method to handle SIGTERM and SIGHUP.
        signal.signal(signal.SIGTERM, self.catch)
        signal.signal(signal.SIGHUP, self.catch)
        # Initialize pigpio object for PWM.
        self.gpio = pigpio.pi()
        # Initialize both LCD displays.
        self.home_lcd = LCDDisplay(25, 0, 12, self.gpio)
        self.away_lcd = LCDDisplay(23, 1, 13, self.gpio)
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

    # Update the LCD displays.
    def updateLCD(self):
        # Extra kwargs to pass to display function.
        kwargs = dict()
        # If game is over or final, add winner as a kwarg for the display function.
        if self.sb.game_status == 'Game Over' or self.sb.game_status == 'Final':
            kwargs['winner'] = self.sb.get_winner()
        # Update the display.
        self.lcd_ctl.display_team_logos(self.sb.home_team_name, self.sb.away_team_name, **kwargs)
        # Signify that the display should be on.
        self.displays_on = True

    # Catch kill signals and subsequently shut down the daemon.
    def catch(self, signum, frame):
        # Shut down both controllers.
        self.segment_ctl.shut.set()
        del self.segment_ctl
        del self.lcd_ctl

    # Main loop, manages everything.
    def run(self):
        # Run all initialization tasks.
        self.init()
        # Run indefinitely, until kill signal is caught and handled by catch method.
        while True:
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
                    sleep(600)
                    continue
            # There is a live game if the execution reaches here.
            # Get a game from the queue and see if that game is already being displayed.
            game = self.active_games.q.get()
            # If this is the first time through or a new game is to be displayed, reset this class's game object.
            if self.game is None or game.game_id != self.game.game_id:
                self.game = game
            # Try to update the scoreboard and get changes.
            try:
                changes = self.sb.update(game.game_id)
            # If there is an error getting the scoreboard, continue to next game.
            except (URLError, ValueError, XMLSyntaxError):
                continue
            # If a new game or status change, update the LCD displays.
            if 'new_game' in changes or 'status' in changes:
                self.updateLCD()
            # Update the segment displays.
            self.segment_ctl.q.put(changes, block=False)
            # Wait before refreshing or moving to the next game.
            sleep(10)


if __name__ == '__main__':
    daemon = CubbieBoardDaemon('/tmp/cubbie-board.pid', stdout='debug/stdout.txt', stderr='debug/stderr.txt')
    daemon.run()
