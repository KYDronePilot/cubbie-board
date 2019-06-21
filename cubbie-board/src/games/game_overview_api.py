"""
For holding the API manager for game overview details.

"""

import json

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
        # Make the request.
        result = GameOverviewAPI.post_request_wrapper(
            self.url,
            json.dumps(game_ids, separators=(',', ':')),
            headers
        )
        # Parse response.
        json_response = json.loads(result.content)
        # If API failed, return nothing.
        # TODO: Add logging!!
        if isinstance(json_response, dict) and 'message' in json_response:
            return []
        # DEBUG: Find what is causing the overview API to return unicode numbers sometimes.
        for game in json_response:
            if isinstance(unicode, game['inning']) or isinstance(unicode, game['home_team_runs']) \
                    or isinstance(unicode, game['away_team_runs']):
                print('ASCII', json.dumps(json_response))
                print('Unicode', json.dumps(json_response, ensure_ascii=False))
                raise ValueError('Unicode error encountered')
        # Create info instances and return.
        return [
            GameOverview(
                game['game_id'],
                game['status'],
                int(game['inning']),
                game['inning_state'],
                int(game['home_team_runs']),
                int(game['away_team_runs']),
                game['home_team_name'],
                game['away_team_name'],
                game['time_date'],
                game['ampm']
            ) for game in json_response
        ]
