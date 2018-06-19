from mlbgame import overview


# from datetime import datetime

# Hold game information needed by peripherals.
class Scoreboard:
    def __init__(self, game_id):
        # Store game_id as a member.
        self.game_id = game_id
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
        # Try to get a new overview object.
        try:
            stats = overview(self.game_id)
        except ValueError:
            # TODO take steps to try and get the game that should be played right now.
            pass
        return stats

    # Get the initial important information about the game; the team names.
    def initialize(self):
        # Get a new overview object.
        stats = self.refreshOverview()
        # Update members.
        self.away_team_name = stats.away_team_name
        self.home_team_name = stats.home_team_name

    # For getting updates on the current score, inning, and game status.
    def updateLive(self):
        # Refresh the overview object.
        stats = self.refreshOverview()
        # Empty dict for any updates.
        changes = dict()
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
        # No need to append to changes, as the segment displays don't need this information.
        if self.game_status != stats.status:
            self.game_status = stats.status
        return changes
