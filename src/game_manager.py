"""
Module for managing games.

"""

from datetime import date
from typing import List, Dict
from .day_game_info import DayGameInfo
from .day_game_info_api import DayGameInfoAPI
from .game_overview import GameOverview
from .game_overview_api import GameOverviewAPI
from Queue import Queue
from decouple import config

# API URL and key.
API_URL = config('DAY_GAME_INFO_API_URL')
API_KEY = config('API_KEY')


class GameManager(object):
    """
    For managing games on a particular day.

    Attributes:
        current_date (date): Date of games to manage
        games (List[DayGameInfo]): Day game info for each game this day
        overviews (List[GameOverview]): Game overviews for each game this day
        current_game_index (int): Index of current game
        preferred_team (str): Name of user's preferred team
        preferred_game (DayGameInfo): Day game info of preferred team's game
        day_game_info_api (DayGameInfoAPI): API for retrieving games on a day
        game_overview_api (GameOverviewAPI): API for retrieving overview of games

    """

    def __init__(self, current_date, preferred_team):
        # type: (date, str) -> None
        """
        Construct game manager for a particular day.

        Args:
            current_date (date): Date of games to manage
            preferred_team (str): The preferred team which supersedes all others

        """
        # Set attributes.
        self.current_date = current_date  # type: date
        self.preferred_team = preferred_team  # type: str
        self.overviews = []  # type: List[GameOverview]
        # Set up APIs.
        self.day_game_info_api = DayGameInfoAPI(API_URL, API_KEY)  # type: DayGameInfoAPI
        self.game_overview_api = GameOverviewAPI(API_URL, API_KEY)  # type: GameOverviewAPI
        # Get games for the current date.
        self.games = self.day_game_info_api.fetch_games(
            current_date.month,
            current_date.day,
            current_date.year
        )  # type: List[DayGameInfo]

    def refresh_overviews(self):
        """
        Refresh each of the game overviews.

        Notes:
            TODO: Efficiency could be improved by only updating those overviews that need it.

        """
        self.overviews = self.game_overview_api.fetch_overviews(
            [game.game_id for game in self.games]
        )



