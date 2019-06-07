"""
Main python module for running the scoreboard.

"""

from src.game_manager import GameManager
from src.lcd_controller import LcdController
from src.segment_controller import SegmentController
from datetime import date
import time
from datetime import date, timedelta
from decouple import config


class CubbieBoard(object):
    """
    Main cubbie board management class.

    Attributes:
        preferred_team (str): The user's preferred team
        game_manager (GameManager): Game info manager
        lcd_controller (LcdController): Controller for LCD displays
        segment_controller (SegmentController): Controller for 7-segment displays

    """

    def __init__(self):
        """
        Setup the scoreboard.

        """
        self.preferred_team = config('PREFERRED_TEAM')  # type: str
        # Setup the game manager.
        self.game_manager = self.setup_game_manager()  # type: GameManager
        # Setup LCD controller.
        self.lcd_controller = LcdController()  # type: LcdController
        # Setup 7-segment display controller.
        self.segment_controller = SegmentController()  # type: SegmentController
        self.segment_controller.start()

    def setup_game_manager(self):
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

    def run(self):
        """
        Main execution loop.

        Returns:
            None

        """
        for i in range(4):
            # Get the next game to display.
            next_game = self.game_manager.get_next_game()
            # If none, exit.
            if next_game is None:
                return
            # Update LCD displays.
            self.lcd_controller.display_team_logos(next_game.home_team_name, next_game.away_team_name)
            # Update segment displays.
            self.segment_controller.write_update('inning', next_game.inning)
            self.segment_controller.write_update('inning_state', next_game.inning_state)
            self.segment_controller.write_update('home_team_runs', next_game.home_team_runs)
            self.segment_controller.write_update('away_team_runs', next_game.away_team_runs)
            # Wait 10 seconds.
            time.sleep(10)
        # Prepare for script shutdown.
        self.lcd_controller.exit()
        self.segment_controller.exit()


if __name__ == '__main__':
    main = CubbieBoard()
    main.run()
