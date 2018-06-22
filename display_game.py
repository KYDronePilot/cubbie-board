from lcd_display import LogoDisplay
from scoreboard import Scoreboard
from sys import argv, exit
from time import sleep
import segment_display
from update_seg_disp import SegmentUpdater
from Queue import Queue

# Get the game ID as the one and only argument accepted by this script.
game_id = argv[1]
# Get a scoreboard object, and initialize both lcd displays.
sb = Scoreboard(game_id)
home_lcd = LogoDisplay(25, 0)
away_lcd = LogoDisplay(23, 1)
# Create segment display objects for the home, away, and inning displays.
home_segment = segment_display.MCP23008(1, 0x20)
away_segment = segment_display.MCP23008(1, 0x22)
inning_segment = segment_display.MCP23008(1, 0x24)
# Queue to pass score and inning changes to the segment updater class.
q = Queue(maxsize=2)
# Object that handles updating the segment displays.
segment_updater = SegmentUpdater(home_segment, away_segment, inning_segment, 4, 17, q)
# Start the segment updater thread.
segment_updater.start()
# Get the initial important values stored in the scoreboard object; the team names.
sb.initialize()
home_lcd.dispLogo(sb.home_team_name)
away_lcd.dispLogo(sb.away_team_name)


# Main loop.
def main():
    # Run loop which updates the scoreboard until game ends.
    while sb.game_status != 'Game Over':
        # Update the scoreboard and get the changes in a dict.
        changes = sb.updateLive()
        # If there are changes, pass them to the segment display updater queue.
        if changes != {}:
            q.put(changes, True)
        # Wait 10 seconds before scanning again.
        sleep(10)
    # TODO add other post-game operations, like displaying a Cubs 'W' logo when the Cubs win.


# TODO configure for when game gets delayed.
try:
    main()
# Stop main when there is a keyboard interruption.
except KeyboardInterrupt:
    pass

# Close SegmentUpdater object.
segment_updater.shut.set()
del segment_updater

