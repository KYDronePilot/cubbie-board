"""
For holding the API manager for game overview details.

"""

import json

import requests
from typing import List

from .base_api import BaseAPI
from .game_overview import GameOverview


class GameOverviewAPI(BaseAPI):
    """
    The game overview API manager.

    """

    def fetch_overviews(self, game_ids):
        # type: (List[str]) -> List[GameOverview]
        """
        Fetch overviews for multiple games.

        Args:
            game_ids (List[str]): IDs of games

        Returns:
            List[GameOverview]: Overviews for each game

        """
        # Headers for request.
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        # Make request.
        # TODO: Make a retry wrapper for continually pounding at the URL until the API answers.
        # TODO: Exception received: requests.exceptions.ConnectionError
        result = requests.post(
            self.url,
            data=json.dumps(game_ids, separators=(',', ':')),
            headers=headers
        )
        # Parse response.
        json_response = json.loads(result.content)
        # If API failed, return nothing.
        # TODO: Add logging!!
        if isinstance(json_response, dict) and 'message' in json_response:
            return []
        # Create info instances and return.
        return [
            GameOverview(
                game['game_id'],
                game['status'],
                game['inning'],
                game['inning_state'],
                game['home_team_runs'],
                game['away_team_runs'],
                game['home_team_name'],
                game['away_team_name'],
                game['time_date'],
                game['ampm']
            ) for game in json_response
        ]
