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
        # Get a new overview object and return it.
        stats = overview(self.game_id)
        return stats

    # For getting updates on the current score, inning, and game status for a game_id.
    def update(self, game_id):
        # Empty dict for any updates.
        changes = dict()
        # Check if the provided game_id is different from the current one.
        if game_id != self.game_id:
            # If they don't match, add 'new_game' key to changes and update game_id.
            changes['new_game'] = None
            self.game_id = game_id
        # Refresh the overview object.
        stats = self.refreshOverview()
        # Update home and away team names.
        self.home_team_name = stats.home_team_name
        self.away_team_name = stats.away_team_name
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
        if self.game_status != stats.status:
            changes['status'] = stats.status
            self.game_status = stats.status
        return changes

    # Determine the winner of a game.
    def getWinner(self):
        # If home team has more runs, return tuple of home and team name, else away and team name.
        if self.home_team_runs > self.away_team_runs:
            return 'home', self.home_team_name
        return 'away', self.away_team_name
