from mlbgame import day, overview
#from datetime import datetime

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
        self.inning = 1
        self.inning_state = 'Top'
        self.game_status = 'PRE_GAME'
    
    # Update scoreboard.
    def update(self):
        # Try to get a new overview object.
        try:
            stats = overview(self.game_id)
        except ValueError:
            # TODO take steps to try and get the game that should be played right now.
        # Update members.
        self.away_team_name = stats.away_team_name
        self.home_team_name = stats.home_team_name
        self.away_team_runs = stats.away_team_runs
        self.home_team_runs = stats.home_team_runs
        self.inning = stats.inning
        self.inning_state = stats.inning_state
        self.game_status = stats.status