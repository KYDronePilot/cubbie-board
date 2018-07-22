# For managing a list of active games that can be scrolled through on the display.
import mlbgame
from Queue import Queue
from urllib2 import URLError

from datetime import datetime, timedelta
import pytz
from scoreboard import Scoreboard

# TODO move to a .conf file.
ET_TZ = 'US/Eastern'


# Maintain a list of active games.
class ActiveGames:
    def __init__(self, pref_team):
        # Preferred team that will supersede all others when live.
        self.pref_team = pref_team
        # Queue of active games. Maxsize of 16 since there can never be more than 15 games at once.
        self.q = Queue(maxsize=16)
        # List of final game game_ids that should be disregarded.
        self.old_finals = list()
        # Scoreboard used to retrieve elapsed time.
        self.sb = Scoreboard()

    # Get current Eastern time, the timezone associated with the mlbgame api.
    def now(self):
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now.astimezone(pytz.timezone(ET_TZ))

    # Fill queue with active games when called. If preferred team is playing, only put in that game.
    def refill(self):
        # Clear the queue safely.
        with self.q.mutex:
            self.q.queue.clear()
        # Grab the current time.
        now = self.now()
        # Get all games for this day.
        games = mlbgame.day(now.year, now.month, now.day)
        # Grab active games.
        active_games = [game for game in games if game.game_status == 'IN_PROGRESS']
        # Get final games that are within 15 minutes of ending and attach to the end of active games.
        active_games += self.getFinals(games)
        # If preferred team is in the list, only put them in the queue.
        for game in active_games:
            if game.away_team == self.pref_team or game.home_team == self.pref_team:
                self.q.put(game, block=False)
                break
        # If the preferred team wasn't in the list, put all the other teams in the queue.
        if self.q.empty():
            for game in active_games:
                self.q.put(game, block=False)

    # Return final games within 15 minutes of ending.
    def getFinals(self, games):
        # List of games within 15 minutes of ending.
        matching_games = list()
        # Get all final games.
        final = [game for game in games if game.game_status == 'FINAL']
        # Determine which games are within range.
        for game in final:
            # If game already determined to be past 15 after final, disregard.
            if game.game_id in self.old_finals:
                continue
            # Try to get a scoreboard object.
            try:
                self.sb.game_id = game.game_id
                sb = self.sb.refreshOverview()
            # If there is an error getting the scoreboard, continue to next game.
            except URLError:
                continue
            # Get starting ET date time with AM or PM attached to the end.
            start_time = "{0} {1}".format(sb.time_date, sb.ampm)
            # Get time elapsed since game begun.
            elapsed_time = sb.elapsed_time
            # Create an ET timezone-aware datetime object for start time.
            start = datetime.strptime(start_time, "%Y/%m/%d %I:%M %p")
            start = pytz.timezone(ET_TZ).localize(start)
            # Retrieve hours and minutes of elapsed time in string form.
            hours, minutes = elapsed_time.split(':')
            # Finally, get the ending time of the game after converting hour and min to int.
            end_time = start + timedelta(hours=int(hours), minutes=int(minutes))
            # Get timedelta between now and when the game ended.
            delta = self.now() - end_time
            # If time has been more than 15 minutes, add id to list of old finals and remove.
            if delta.seconds // 60 > 15:
                self.old_finals.append(game.game_id)
            # Otherwise, add game to list of matching games.
            else:
                matching_games.append(game)
        return matching_games
