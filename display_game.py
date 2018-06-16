from mlbgame import day, overview
from lcd_display import LogoDisplay
from scoreboard import Scoreboard
from sys import argv
from time import sleep

# Get the game ID as the one and only argument accepted by this script.
game_id = argv[1]
# Get a scoreboard object, and initialize both lcd displays.
sb = Scoreboard(game_id)
home_disp = LogoDisplay(25, 0)
away_disp = LogoDisplay(23, 1)
# Get an initial update of the scoreboard and display team logos.
sb.update()
home_disp.dispLogo(sb.home_team_name)
away_disp.dispLogo(sb.away_team_name)

# Run main loop which updates the scoreboard until game ends.
# TODO configure for when game gets delayed.
while sb.game_status != 'FINAL':
    # Update the scoreboard object.
    sb.update()
    # TODO update inning and score displays.
    sleep(10)