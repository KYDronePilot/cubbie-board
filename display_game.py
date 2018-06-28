from lcd_display.lcd_display import LogoDisplay
from scoreboard import Scoreboard
from sys import argv
from time import sleep
import segment_display
from update_seg_disp import SegmentUpdater
from Queue import Queue
import pigpio
from lcd_display.lcd_controller import LcdController

# Get the game ID as the one and only argument accepted by this script.
game_id = argv[1]
# Initialize pigpio object for PWM.
gpio = pigpio.pi()
# Get a scoreboard object, and initialize both lcd displays.
sb = Scoreboard(game_id)
home_lcd = LogoDisplay(25, 0, 12, gpio)
away_lcd = LogoDisplay(23, 1, 13, gpio)
# Create segment display objects for the home, away, and inning displays.
home_segment = segment_display.MCP23008(1, 0x21)
away_segment = segment_display.MCP23008(1, 0x20)
inning_segment = segment_display.MCP23008(1, 0x24)
# Queue to pass score and inning changes to the segment updater class.
q = Queue(maxsize=2)
# Object that handles updating the segment displays.
segment_updater = SegmentUpdater(home_segment, away_segment, inning_segment, 17, 4, q)
# Get the initial important values stored in the scoreboard object; the team names.
sb.initialize()
# Give the LCD display objects to their controller.
lcd_ctl = LcdController(home_lcd, away_lcd)
# Initialize LCD displays.
lcd_ctl.init(sb.home_team_name, sb.away_team_name)
# Start the segment updater thread.
segment_updater.start()


# Main loop.
def main():
    # Run loop which updates the scoreboard until game ends.
    while True:
        # Update the scoreboard and get the changes in a dict.
        changes = sb.updateLive()
        # If there are changes, pass them to the segment display updater queue.
        if changes != {}:
            q.put(changes, True)
        # Wait 10 seconds before scanning again.
        sleep(10)
    # TODO add other post-game operations, like displaying a Cubs 'W' logo when the Cubs win.


# TODO configure for when game gets delayed.
#try:
main()
# Stop main when there is a keyboard interruption.
#except:
#    pass

# Close SegmentUpdater object.
#segment_updater.shut.set()
#del segment_updater
