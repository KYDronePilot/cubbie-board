"""
Main python module for running the scoreboard.

"""

import os
import signal
import sys
import time
from datetime import date, timedelta

from decouple import config
from typing import ClassVar

# Setup src path.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from games.game_manager import GameManager
from games.game_overview import GameOverview
from lcd_display.lcd_controller import LcdController
from segment_display.segment_controller import SegmentController


class CubbieBoard(object):
    """
    Main cubbie board management class.

    Attributes:
        preferred_team (str): The user's preferred team
        game_manager (GameManager): Game info manager
        lcd_controller (LcdController): Controller for LCD displays
        segment_controller (SegmentController): Controller for 7-segment displays

    """

    # Timeout when no games to display.
    SCAN_TIMEOUT = 300  # type: ClassVar[int]

    def __init__(self):
        """
        Setup the scoreboard.

        """
        self.preferred_team = config('PREFERRED_TEAM')  # type: str
        # Setup the game manager.
        self.game_manager = self._setup_game_manager()  # type: GameManager
        # Setup LCD controller.
        self.lcd_controller = LcdController()  # type: LcdController
        # Setup 7-segment display controller.
        self.segment_controller = SegmentController()  # type: SegmentController
        self.segment_controller.start()
        # Register exit signal handler.
        signal.signal(signal.SIGINT, self.exit_signal_handler)
        signal.signal(signal.SIGHUP, self.exit_signal_handler)
        signal.signal(signal.SIGTERM, self.exit_signal_handler)

    def _setup_game_manager(self):
        # type: () -> GameManager
        """
        Setup the current game manager.

        Returns:
            GameManager: The current game manager

        """
        # Get manager for current day.
        today_game_manager = GameManager(date.today(), self.preferred_team)
        # If no games available, get manager for previous day.
        if today_game_manager.get_next_game() is None:
            yesterday_game_manager = GameManager(date.today() - timedelta(days=1), self.preferred_team)
            # If a game is available, use that manager.
            if yesterday_game_manager.get_next_game() is not None:
                return yesterday_game_manager
        return today_game_manager

    def _update_game_manager(self):
        # type: () -> None
        """
        Update the game manager, switching to the next day if necessary.

        Returns:
            None

        """
        # If on different day then manager, get new manager for next day.
        if self.game_manager.current_date.day != date.today().day:
            self.game_manager = GameManager(date.today(), self.preferred_team)
        # Else, turn off displays and wait before continuing.
        else:
            self.lcd_controller.turn_off_displays()
            self.segment_controller.turn_off_displays()
            time.sleep(CubbieBoard.SCAN_TIMEOUT)

    def _update_displays(self, new_overview):
        # type: (GameOverview) -> None
        """
        Update the displays with a new overview.

        Returns:
            None

        """
        # Update LCD displays.
        self.lcd_controller.display_team_logos(new_overview)
        # Update segment displays.
        self.segment_controller.write_update('inning', new_overview.inning)
        self.segment_controller.write_update('inning_state', new_overview.inning_state)
        self.segment_controller.write_update('home_team_runs', new_overview.home_team_runs)
        self.segment_controller.write_update('away_team_runs', new_overview.away_team_runs)

    def exit_signal_handler(self, sig, frame):
        """
        Signal handler for exiting the program.

        Args:
            sig: The signal
            frame: The frame

        Returns:
            None

        """
        print('Exiting')
        self.lcd_controller.exit()
        self.segment_controller.exit()
        exit(0)

    def run(self):
        """
        Main execution loop.

        Returns:
            None

        """
        while True:
            # Get the next game to display.
            next_game = self.game_manager.get_next_game()
            # If none, update the manager and try again.
            if next_game is None:
                self._update_game_manager()
                continue
            # Update displays with next game.
            self._update_displays(next_game)
            # Wait 10 seconds before repeating.
            time.sleep(10)


if __name__ == '__main__':
    main = CubbieBoard()
    main.run()
