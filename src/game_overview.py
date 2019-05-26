"""
For holding overview info about a game.

"""

from datetime import datetime


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
