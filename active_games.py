# For managing a list of active games that can be scrolled through on the display.
import mlbgame
import re
from Queue import Queue
from urllib2 import URLError
from time import sleep

from datetime import datetime, timedelta
import pytz
from scoreboard import Scoreboard

# TODO move to a .conf file.
ET_TZ = 'US/Eastern'


# Convert list of hours and minutes in str type to tuple of hours and minutes in int type.
def hours_minutes_convert(time):
    """

    :type time: list
    """
    # Get hours and minutes from the time list.
    hours, minutes = time
    # If either is an empty string, treat as a 0.
    if not hours:
        hours = 0
    if not minutes:
        minutes = 0
    # Return hours and minutes, casted to int.
    return int(hours), int(minutes)


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
    # TODO if there are no active games for the day, check the previous day (for games that go late into the night).
    def refill(self):
        # Clear the queue safely.
        with self.q.mutex:
            self.q.queue.clear()
        # Grab the current time.
        now = self.now()
        # Try to get all games for this day.
        while True:
            try:
                games = mlbgame.day(now.year, now.month, now.day)
                break
            # If mlbgame fails to pull the games, wait a little bit and try again.
            except URLError:
                sleep(10)
                # DEBUG.
                print('Failed to pull games for the day, trying again...')
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
            # If the elapsed_time field is empty, consider game over and append to list of old finals.
            if not sb.elapsed_time:
                self.old_finals.append(game.game_id)
                continue
            # Get starting ET date time with AM or PM attached to the end.
            start_time = "{0} {1}".format(sb.time_date, sb.ampm)
            # Create an ET timezone-aware datetime object for start time.
            start = datetime.strptime(start_time, "%Y/%m/%d %I:%M %p")
            start = pytz.timezone(ET_TZ).localize(start)
            # Check if time delayed is specified.
            # Format of extra delay message: "2:55 (1:35 delay)"
            if 'delay' in sb.elapsed_time:
                # Capture time text in parentheses.
                delay_time = re.findall('(?<=\().*?(?=\))', sb.elapsed_time)
                # Future potential help: throw exception if more than one parentheses pair.
                if len(delay_time) > 1:
                    raise ValueError('More than one parentheses pair in elapsed time: {0}'.format(sb.elapsed_time))
                # Chop off the ' delay' part and retrieve the hours and minutes as a list.
                delay_time = delay_time[0][:-6].split(':')
                # Get the actual duration hours and minutes from the beginning of the string as a list.
                dur_time = re.findall('.*?(?= \()', sb.elapsed_time)[0].split(':')
                # Convert both delay and durations times to int type hours and minutes.
                delay_hours, delay_minutes = hours_minutes_convert(delay_time)
                dur_hours, dur_minutes = hours_minutes_convert(dur_time)
                # Add up minutes from both times.
                minutes = delay_minutes + dur_minutes
                # Add up hours plus any whole hours in the minutes var.
                hours = delay_hours + dur_hours + (minutes / 60)
                # Get remaining minutes after taking out any whole hours.
                minutes %= 60
            # If no delay in game, extra hours and minutes here.
            else:
                # Retrieve hours and minutes of elapsed time in list form.
                time = sb.elapsed_time.split(':')
                # Convert hours and minutes to int type.
                hours, minutes = hours_minutes_convert(time)
            # Finally, get the ending time of the game after converting hour and min to int.
            end_time = start + timedelta(hours=hours, minutes=minutes)
            # Get timedelta between now and when the game ended.
            delta = self.now() - end_time
            # If time has been more than 15 minutes, add id to list of old finals and remove.
            if delta.seconds // 60 > 15:
                self.old_finals.append(game.game_id)
            # Otherwise, add game to list of matching games.
            else:
                matching_games.append(game)
        return matching_games
