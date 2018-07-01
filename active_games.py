# For managing a list of active games that can be scrolled through on the display.
import mlbgame
import threading
from time import sleep

from datetime import datetime
import pytz

# TODO move to a .conf file.
ET_TZ = 'US/Eastern'
PREFERRED_TEAM = 'Cubs'


# Maintain a list of active games.
class ActiveGames(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # List of active games to be checked by external modules.
        self.active_games = list()
        # Handle to shut down the thread.
        self.shut = threading.Event()
        # Get object for current time in the Eastern Time Zone, since the the mlbgame times
        # are in that time zone.
        utc_now = pytz.utc.localize(datetime.utcnow())
        self.et_tz = utc_now.astimezone(pytz.timezone(ET_TZ))

    # Check what games are active every 5 minutes.
    def run(self):
        # Run till stopped.
        while not self.shut.is_set():
            # Grab the current time.
            now = self.et_tz.now()
            # Grab the games going on right now.
            self.active_games = [game for game in mlbgame.day(now.year, now.month, now.day) if
                                 game.game_status == 'IN_PROGRESS']
            # If the preferred team is in the mix, eliminate all others.
            for game in self.active_games:
                if game.away_team == PREFERRED_TEAM or game.home_team == PREFERRED_TEAM:
                    self.active_games = [game]
                    break
            # Wait 5 minutes before checking again.
            sleep(300)
