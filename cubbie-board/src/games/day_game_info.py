"""
Module for managing the API which gets day-based game info.

"""

from datetime import datetime

from typing import ClassVar


class DayGameInfo(object):
    """
    Day-based game info API manager.

    Attributes:
        game_id (str): ID of game
        date (datetime): Game start time (Eastern time)
        game_start_time (str): AM/PM based game start time (Eastern time)
        game_status (str): Status of the game
        home_team (str): The home team
        away_team (str): The away team

    """

    # Game status constants.
    PRE_GAME_STATUS = 'PRE_GAME'  # type: ClassVar[str]
    IN_PROGRESS_STATUS = 'IN_PROGRESS'  # type: ClassVar[str]
    FINAL_STATUS = 'FINAL'  # type: ClassVar[str]

    def __init__(self, game_id, date, game_start_time, game_status, home_team, away_team):
        # type: (str, str, str, str, str, str) -> None
        """
        Construct day-based game info.

        Args:
            game_id (str): ID of game
            date (str): Game date in ISO format (Eastern time)
            game_start_time (str): AM/PM based game start time (Eastern time)
            game_status (str): Status of the game
            home_team (str): The home team
            away_team (str): The away team

        """
        self.game_id = game_id  # type: str
        # Convert to datetime.
        self.date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')  # type: datetime
        self.game_start_time = game_start_time  # type: str
        self.game_status = game_status  # type: str
        self.home_team = home_team  # type: str
        self.away_team = away_team  # type: str

    def is_active(self):
        # type: () -> bool
        """
        Checks if the game is active.

        Returns:
            bool: Whether or not the game is active

        """
        return self.game_status == DayGameInfo.IN_PROGRESS_STATUS

    def is_final(self):
        # type: () -> bool
        """
        Checks if the game is over.

        Returns:
            bool: Whether or not the game is over

        """
        return self.game_status == DayGameInfo.FINAL_STATUS

    def is_pre_game(self):
        # type: () -> bool
        """
        Checks if game is in pre-game.

        Returns:
            bool: Whether or not the game is in pre-game

        """
        return self.game_status == DayGameInfo.PRE_GAME_STATUS
