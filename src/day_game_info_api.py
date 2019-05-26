import json

import requests
from typing import List

from src.day_game_info import DayGameInfo
from .base_api import BaseAPI


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
        result = requests.post(self.url, data=json.dumps(request_data, separators=(',', ':')), headers=headers)
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