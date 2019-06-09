"""
Module for managing games.

"""

from Queue import Queue
from datetime import date

from decouple import config
from typing import List, Union

from .day_game_info import DayGameInfo
from .day_game_info_api import DayGameInfoAPI
from .game_overview import GameOverview
from .game_overview_api import GameOverviewAPI

# API URL and key.
DAY_GAME_INFO_API_URL = config('DAY_GAME_INFO_API_URL')
GAME_OVERVIEW_API_URL = config('GAME_OVERVIEW_API_URL')
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
        overview_queue (Queue): Queue of overviews to display next.

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
        self.overview_queue = Queue()  # type: Queue
        self.overviews = []  # type: List[GameOverview]
        # Set up APIs.
        self.day_game_info_api = DayGameInfoAPI(DAY_GAME_INFO_API_URL, API_KEY)  # type: DayGameInfoAPI
        self.game_overview_api = GameOverviewAPI(GAME_OVERVIEW_API_URL, API_KEY)  # type: GameOverviewAPI
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

    def _update_overviews(self):
        # type: () -> int
        """
        Update game overviews.

        Notes:
            If preferred team not active, update everything not final else, update just their game.

        Returns:
            int: Index of preferred team's game if active, -1 if not

        """
        # Whether the preferred team is actively playing.
        pref_team_active = False
        # For determining which game overviews to update.
        do_update = [False] * len(self.overviews)
        # Get index for preferred team if playing.
        pref_team_i = self._get_team_overview_i(self.preferred_team)
        # If not -1 and active, set as the only game to update.
        if pref_team_i != -1 and self.overviews[pref_team_i].is_active():
            pref_team_active = True
            do_update[pref_team_i] = True
        # Else, set to update the games that are not final.
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
        # If preferred team active, return index.
        if pref_team_active:
            return pref_team_i
        return -1

    def _refill_queue(self, pref_team_i=-1):
        # type: (int) -> None
        """
        Refill the queue of games to display.

        Args:
            pref_team_i (int): Index of preferred team if active, -1 if not active.

        Returns:
            None

        """
        # If active preferred team, just add it.
        if pref_team_i != -1:
            self.overview_queue.put(self.overviews[pref_team_i])
        # Otherwise, refill with games that should be displayed.
        else:
            for overview in self.overviews:
                if overview.should_display_game():
                    self.overview_queue.put(overview)

    def _are_all_final(self):
        # type: () -> bool
        """
        Check if all the overviews are final.

        Returns:
            bool: Whether or not all the overviews are final

        """
        cnt = 0
        for game in self.overviews:
            if game.is_final():
                cnt += 1
        return cnt == len(self.overviews)

    def refresh_overviews(self):
        # type: () -> None
        """
        Update games and refill the game queue.

        Notes:
            If preferred team is active, only update and refill that game.

        Returns:
            None

        """
        # Update games, getting preferred team game index if active.
        pref_team_i = self._update_overviews()
        # Refill game queue if not all games are final.
        if not self._are_all_final():
            self._refill_queue(pref_team_i=pref_team_i)

    def get_next_game(self):
        # type: () -> Union[None, GameOverview]
        """
        Get overview of next game to display, refreshing if necessary.

        Returns:
            Union[None, GameOverview]: Next overview to display if exists, None if not

        """
        # If not empty, get next game.
        if not self.overview_queue.empty():
            return self.overview_queue.get()
        # Else, refresh and try again.
        self.refresh_overviews()
        if not self.overview_queue.empty():
            return self.overview_queue.get()
        return None
