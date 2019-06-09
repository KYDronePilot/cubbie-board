import json

from typing import List

from .base_api import BaseAPI
from .day_game_info import DayGameInfo


class DayGameInfoAPI(BaseAPI):
    """
    Day-based game info API manager.

    """

    def fetch_games(self, month, day, year):
        # type: (int, int, int) -> List[DayGameInfo]
        """
        Fetch API info for a specific day.

        Args:
            month (int): Month of day
            day (int): The day
            year (int): Year of day

        Returns:
            List[DayGameInfo]: Info for each game

        """
        # Format request data.
        request_data = {
            'month': month,
            'day': day,
            'year': year
        }
        # Headers for request.
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        # Make the request.
        result = DayGameInfoAPI.post_request_wrapper(
            self.url,
            json.dumps(request_data, separators=(',', ':')),
            headers
        )
        # Parse response.
        json_response = json.loads(result.content)
        # If API failed, return nothing.
        # TODO: Add logging!!
        if isinstance(json_response, dict) and 'message' in json_response:
            return []
        # Create info instances and return.
        return [
            DayGameInfo(
                game['game_id'],
                game['date'],
                game['game_start_time'],
                game['game_status'],
                game['home_team'],
                game['away_team']
            ) for game in json_response
        ]
