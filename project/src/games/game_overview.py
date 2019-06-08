"""
For holding overview info about a game.

Notes:
    TODO: Add method for "is_scheduled".

"""

from datetime import datetime

from typing import ClassVar


class GameOverview(object):
    """
    For holding overview info of a game.

    Attributes:
        game_id (str): ID of game
        status (str): Game status
        inning (int): Current inning
        inning_state (str): Current inning state
        home_team_runs (int): Home team runs
        away_team_runs (int): Away team runs
        home_team_name (str): Home team name
        away_team_name (str): Away team name
        start_time (datetime): Start time of the game

    """

    # Game status constants.
    WARM_UP_STATUS = 'Warmup'  # type: ClassVar[str]
    IN_PROGRESS_STATUS = 'In Progress'  # type: ClassVar[str]
    FINAL_STATUS = 'Final'  # type: ClassVar[str]

    def __init__(
            self,
            game_id,
            status,
            inning,
            inning_state,
            home_team_runs,
            away_team_runs,
            home_team_name,
            away_team_name,
            time_date,
            ampm
    ):
        # type: (str, str, int, str, int, int, str, str, str, str) -> None
        """
        Process api data and save to attributes.

        Args:
            game_id (str): ID of game
            status (str): Game status
            inning (int): Current inning
            inning_state (str): Current inning state
            home_team_runs (int): Home team runs
            away_team_runs (int): Away team runs
            home_team_name (str): Home team name
            away_team_name (str): Away team name
            time_date (str): Date and time of game (no AM/PM info)
            ampm (str): AM/PM info of time

        """
        self.game_id = game_id  # type: str
        self.status = status  # type: str
        self.inning = inning  # type: int
        self.inning_state = inning_state  # type: str
        self.home_team_runs = home_team_runs  # type: int
        self.away_team_runs = away_team_runs  # type: int
        self.home_team_name = home_team_name  # type: str
        self.away_team_name = away_team_name  # type: str
        # Process and set time.
        self.start_time = self._process_time(time_date, ampm)  # type: datetime

    @staticmethod
    def _process_time(time_date, ampm):
        # type: (str, str) -> datetime
        """
        Create datetime from time and AM/PM info.

        Args:
            time_date (str): Time and date info
            ampm (str): AM/PM info

        Returns:
            datetime: Datetime object representing input time

        """
        # Extract time.
        return datetime.strptime(time_date + ' ' + ampm, '%Y/%m/%d %I:%M %p')

    def is_active(self):
        # type: () -> bool
        """
        Checks if the game is active.

        Returns:
            bool: Whether or not the game is active

        """
        return self.status == GameOverview.IN_PROGRESS_STATUS

    def is_final(self):
        # type: () -> bool
        """
        Checks if the game is over.

        Returns:
            bool: Whether or not the game is over

        """
        return self.status == GameOverview.FINAL_STATUS

    def is_warm_up(self):
        # type: () -> bool
        """
        Checks if game is in warm-up.

        Returns:
            bool: Whether or not the game is in warm-up

        """
        return self.status == GameOverview.WARM_UP_STATUS

    def is_playing(self, team):
        # type: (str) -> bool
        """
        Whether a specific team is playing in this game.

        Args:
            team (str): Team to check

        Returns:
            bool: Whether or not the team is playing in this game

        """
        return team == self.home_team_name or team == self.away_team_name
