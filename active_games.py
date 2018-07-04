# For managing a list of active games that can be scrolled through on the display.
import mlbgame
from Queue import Queue

from datetime import datetime
import pytz

# TODO move to a .conf file.
ET_TZ = 'US/Eastern'


# Maintain a list of active games.
class ActiveGames:
    def __init__(self, pref_team):
        # Preferred team that will supersede all others when live.
        self.pref_team = pref_team
        # Queue of active games. Maxsize of 16 since there can never be more than 15 games at once.
        self.q = Queue(maxsize=16)
        # Get object for current time in the Eastern Time Zone, since the the mlbgame times
        # are in that time zone.
        utc_now = pytz.utc.localize(datetime.utcnow())
        self.et_tz = utc_now.astimezone(pytz.timezone(ET_TZ))

    # Fill queue with active games when called. If preferred team is playing, only put in that game.
    def refill(self):
        # Clear the queue safely.
        with self.q.mutex:
            self.q.queue.clear()
        # Grab the current time.
        now = self.et_tz.now()
        # Grab the games going on right now.
        active_games = [game for game in mlbgame.day(now.year, now.month, now.day) if
                             game.game_status == 'IN_PROGRESS']
        # If preferred team is in the list, only put them in the queue.
        for game in active_games:
            if game.away_team == self.pref_team or game.home_team == self.pref_team:
                self.q.put(game, block=False)
                break
        # If the preferred team wasn't in the list, put all the other teams in the queue.
        if self.q.empty():
            for game in active_games:
                self.q.put(game, block=False)
