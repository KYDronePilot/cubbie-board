import threading
from typing import Dict, List, Any
import json

import mlbgame


class GameInfoFetcher(threading.Thread):
    """
    For making overview fetching run in parallel.

    Attributes:
        game_id (str): ID of the game in question
        game_info (Dict[str, Any]): Retrieved game info

    """

    game_id: str
    game_info: Dict[str, Any]

    def __init__(self, game_id: str) -> None:
        """
        Basic thread constructor.

        Args:
            game_id (str): ID of game in question

        """
        threading.Thread.__init__(self)
        self.game_id = game_id

    def get_game_info(self) -> Dict[str, Any]:
        """
        Get info for a particular game ID.

        Returns:
            Dict[str, Any]: Game info in JSON format

        """
        # Get the overview.
        overview = mlbgame.overview(self.game_id)
        # Return formatted data.
        return {
            'game_id': self.game_id,
            'status': overview.status,
            'inning': overview.inning,
            'inning_state': overview.inning_state,
            'home_team_runs': overview.home_team_runs,
            'away_team_runs': overview.away_team_runs,
            'home_team_name': overview.home_team_name,
            'away_team_name': overview.away_team_name,
            'time_date': overview.time_date,
            'ampm': overview.ampm
        }

    def run(self) -> None:
        """
        Thread wrapper for getting game info.

        Returns:
            None

        """
        self.game_info = self.get_game_info()


def get_multiple_game_info(game_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get info for multiple game IDs.

    Args:
        game_ids (List[str]): IDs of games

    Returns:
        List[Dict[str, Any]]: Game info in JSON format

    """
    # Create the game info workers.
    workers = [GameInfoFetcher(game_id) for game_id in game_ids]
    # Start the worker threads.
    for worker in workers:
        worker.start()
    # Join them.
    for worker in workers:
        worker.join()
    # Return the game info.
    return [worker.game_info for worker in workers]


def lambda_handler(event, context):
    """
    Handler for AWS lambda calls.

    Args:
        event: The event
        context: Data coming with the event

    Returns:
        List[Dict[str, Any]]: Game info in JSON format

    """
    # Get event data.
    event_data = json.loads(event['body'])
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(
            get_multiple_game_info(event_data),
            separators=(',', ':')
        )
    }
