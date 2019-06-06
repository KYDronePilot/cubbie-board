"""
Main python module for running the scoreboard.

"""

from src.game_manager import GameManager
from src.lcd_controller import LcdController
from src.segment_controller import SegmentController
from datetime import date
import time


class CubbieBoard(object):
    """
    Main cubbie board management class.

    Attributes:
        game_manager (GameManager): Game info manager
        lcd_controller (LcdController): Controller for LCD displays
        segment_controller (SegmentController): Controller for 7-segment displays

    """

    def __init__(self):
        """
        Setup the scoreboard.

        """
        # Setup the game manager.
        self.game_manager = GameManager(date.today(), 'Cubs')  # type: GameManager
        # Setup LCD controller.
        self.lcd_controller = LcdController()  # type: LcdController
        # Setup 7-segment display controller.
        self.segment_controller = SegmentController()  # type: SegmentController
        self.segment_controller.start()

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
