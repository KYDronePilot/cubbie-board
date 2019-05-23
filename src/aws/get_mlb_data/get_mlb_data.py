import json
from typing import Dict, List, Any
import mlbgame
from datetime import datetime


def get_mlb_games() -> List[Dict[str, Any]]:
    """
    Get the MLB games for the current day.

    Notes:
        Returns data in a JSON format.

    Returns:
        List[Dict[str, Any]]

    """
    # Datetime right now.
    now = datetime.now()
    # Get IDs of games today.
    games = mlbgame.day(now.year, now.month, now.day)
    # DEBUG: just return that info.
    return games
