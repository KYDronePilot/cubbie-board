from mlbgame import overview


# For holding live information on a game.
class Scoreboard:
    def __init__(self):
        # Initialize to None, needs to be changed by main daemon before use.
        self.game_id = None
        # Initialize all other members here.
        self.away_team_name = 'blank'
        self.home_team_name = 'blank'
        self.away_team_runs = 0
        self.home_team_runs = 0
        self.inning = 0
        self.inning_state = 'blank'
        self.game_status = 'Warmup'

    # Returns a new overview object.
    def refreshOverview(self):
        # If no game_id specified, raise an error.
        if self.game_id is None:
            raise ValueError('No game_id specified for scoreboard instance')
        # Try to get a new overview object.
        try:
            stats = overview(self.game_id)
        except ValueError:
            # TODO take steps to try and get the game that should be played right now.
            pass
        return stats

    # For getting updates on the current score, inning, and game status.
    def update(self):
        # Refresh the overview object.
        stats = self.refreshOverview()
        # Empty dict for any updates.
        changes = dict()
        # Update home and away team names.
        self.home_team_name = stats.home_team_name
        self.away_team_name = stats.away_team_name
        # Update the game status.
        self.game_status = stats.status
        # If a field changed, append to changes and update its member.
        if self.away_team_runs != stats.away_team_runs:
            changes['away_team_runs'] = stats.away_team_runs
            self.away_team_runs = stats.away_team_runs
        if self.home_team_runs != stats.home_team_runs:
            changes['home_team_runs'] = stats.home_team_runs
            self.home_team_runs = stats.home_team_runs
        if self.inning != stats.inning:
            changes['inning'] = stats.inning
            self.inning = stats.inning
        if self.inning_state != stats.inning_state:
            changes['inning_state'] = stats.inning_state
            self.inning_state = stats.inning_state
        return changes
