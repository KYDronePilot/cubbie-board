import mlbgame
import pytz
from datetime import datetime
import subprocess

# Team that we are interested in seeing on the scoreboard.
my_team = 'Cubs'

# TODO get local timezone.
tz = pytz.timezone('US/Eastern')
# Get the current time.
now = datetime.now(tz)

# Get a list of the games for our team of interest today.
games = mlbgame.day(now.year, now.month, now.day, home=my_team, away=my_team)

for game in games:
    # At command arguments, time to start cubbie board for game.
    at_cmd = "{0} - 15 minutes".format(game.game_start_time)
    # Execute 'at' command, passing command to be executed when game starts.
    schedule = subprocess.Popen(('at', at_cmd), stdin=subprocess.PIPE)
    schedule.communicate(input=b'./display_game.py {0}'.format(game.game_id))