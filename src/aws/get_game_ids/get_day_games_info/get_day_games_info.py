import json
from typing import Dict, List, Any

import mlbgame


def get_day_games_info(month: int, day: int, year: int) -> List[Dict[str, Any]]:
    """
    Get basic info for games on a particular day.

    Args:
        month (int): Month of day
        day (int): The day
        year (int): Year of day

    Returns:
        List[Dict[str, Any]]: Basic game info in JSON format

    """
    # Get basic info for games on the day.
    games = mlbgame.day(year, month, day)
    # Format the info into JSON and return.
    return [
        {
            'game_id': game.game_id,
            'date': game.date.isoformat(),
            'game_start_time': game.game_start_time,
            'game_status': game.game_status,
            'home_team': game.home_team,
            'away_team': game.away_team
        }
        for game in games]


def lambda_handler(event, context):
    """
    Handler for AWS lambda calls.

    Args:
        event: Event data
        context: Event context

    Returns:
        List[Dict[str, Any]]: Basic game info in JSON format

    """
    # Get event data.
    event_data = json.loads(event['body'])
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(get_day_games_info(
            int(event_data['month']),
            int(event_data['day']),
            int(event_data['year'])
        ), separators=(',', ':'))
    }
