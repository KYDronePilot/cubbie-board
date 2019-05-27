"""
Module for managing games.

"""

from datetime import date

from decouple import config
from typing import List

from .day_game_info import DayGameInfo
from .day_game_info_api import DayGameInfoAPI
from .game_overview import GameOverview
from .game_overview_api import GameOverviewAPI

# API URL and key.
API_URL = config('DAY_GAME_INFO_API_URL')
API_KEY = config('API_KEY')


class GameManager(object):
    """
    For managing games on a particular day.

    Attributes:
        current_date (date): Date of games to manage
        games (List[DayGameInfo]): Day game info for each game
        overviews (List[GameOverview]): Game overviews for each game
        current_game_index (int): Index of current game
        preferred_team (str): Name of user's preferred team
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
        # Get overviews for each of the games.
        self.overviews = self.game_overview_api.fetch_overviews(
            [game.game_id for game in self.games]
        )  # type: List[GameOverview]
        # Get index of preferred team.
        preferred_overview_i = self._get_team_overview_i(self.preferred_team)
        # If preferred team playing and active, set as current game.
        if preferred_overview_i != -1 and self.overviews[preferred_overview_i].is_active():
            self.current_game_index = preferred_overview_i  # type: int
        # Else, set to default.
        else:
            self.current_game_index = -1  # type: int

    def _get_team_overview_i(self, team):
        # type: (str) -> int
        """
        Get index of the overview for a specific team.

        Args:
            team (str): The team in question

        Returns:
            int: The team's overview index if exists else, -1

        """
        for i in range(len(self.overviews)):
            # Return index upon seeing matching overview.
            if self.overviews[i].is_playing(team):
                return i
        # Else, team not playing.
        return -1

    def refresh_overviews(self):
        # type: () -> None
        """
        Refresh each of the game overviews.

        Returns:
            None

        """
        # For determining which game overviews to update.
        do_update = [False] * len(self.overviews)
        # Get overview index for preferred team if playing.
        preferred_overview_i = self._get_team_overview_i(self.preferred_team)
        # If not -1 and active, set as the only game to update.
        if preferred_overview_i != -1 and self.overviews[preferred_overview_i].is_active():
            do_update[preferred_overview_i] = True
        # Else, set to update the games that are not over.
        else:
            for i in range(len(self.overviews)):
                if not self.overviews[i].is_final():
                    do_update[i] = True
        # Get game IDs to update.
        update_ids = [self.overviews[i].game_id for i in range(len(self.overviews)) if do_update[i]]
        # Get new overviews.
        new_overviews = self.game_overview_api.fetch_overviews(update_ids)
        # Re-insert new overviews.
        new_i = 0
        for i in range(len(self.overviews)):
            if do_update[i]:
                self.overviews[i] = new_overviews[new_i]
                new_i += 1
