# For updating the 7-segment display.

import threading
import RPi.GPIO as GPIO
from Queue import Queue
from time import sleep

from segment_display import MCP23008

# Number of iterations before checking the queue.
COUNTER = 100

# Main worker function that watches for digit changes, applying as needed and
# blinks the segments if in 2-segment mode.
class SegmentController(threading.Thread):
    def __init__(self, home, away, inning, left_dig_tran, right_dig_tran):
        threading.Thread.__init__(self)
        # For getting updates to this thread.
        self.q = Queue(maxsize=2)
        self.refresh = Refresh(home, away, inning, left_dig_tran, right_dig_tran)
        self.single_mode = True
        self.shut = threading.Event()
        # Initialize with the displays turned off.
        self.refresh.off()
        # Initial set to the right digit.
        GPIO.output(left_dig_tran, GPIO.LOW)
        GPIO.output(right_dig_tran, GPIO.HIGH)
        # Counter for determining if the queue should be checked.
        self.cnt = COUNTER

    # Cleanup the GPIO and shut off the displays on delete.
    def __del__(self):
        GPIO.cleanup()
        self.refresh.off()

    # Actual thread that is run.
    def run(self):
        while not self.shut.is_set():
            # Wait a little bit before checking the counter.
            sleep(0.005)
            # Call cache updater method if counter has reached 0.
            if self.cnt == 0:
                self.update_cache()
            # If not in single digit mode, blink both digits on each display.
            elif not self.single_mode:
                self.refresh.updateDouble()
            # Decrement the counter.
            self.cnt -= 1

    # Update the segment display caches if there is something in the queue.
    def update_cache(self):
        # Exit if the queue is empty.
        if self.q.empty():
            return
        # Reset counter.
        self.cnt = COUNTER
        # Get dictionary of updated values.
        val_dict = self.q.get()
        for key, val in val_dict.items():
            # Update display objects if name and val in the dict.
            if key == 'home_team_runs':
                self.refresh.home.updateCache(val)
            elif key == 'away_team_runs':
                self.refresh.away.updateCache(val)
            elif key == 'inning':
                self.refresh.inning.updateCache(val)
            elif key == 'inning_state':
                # Home display's extra IO pin represents top, away's represents bottom.
                if val == 'Top':
                    self.refresh.home.extra_pin_on = True
                    self.refresh.away.extra_pin_on = False
                elif val == 'Bottom':
                    self.refresh.home.extra_pin_on = False
                    self.refresh.away.extra_pin_on = True
            # Shut off all displays.
            elif key == 'off':
                self.refresh.off()
        # After updating the values, set to the correct segment mode.
        self.checkMode()
        # Depending on the mode, update the display accordingly.
        if self.single_mode:
            self.refresh.updateSingle()
        else:
            self.refresh.updateDouble()

    # Checks current display numbers to determine whether to be in single mode or not.
    def checkMode(self):
        # If all displays' left digits are blank, set to single mode.
        if (
                self.refresh.home.cache_dig_1 == 10 and
                self.refresh.away.cache_dig_1 == 10 and
                self.refresh.inning.cache_dig_1 == 10
        ):
            self.single_mode = True
        # Else, set to 2-segment mode.
        else:
            self.single_mode = False


# Handles refreshing of the displays.
class Refresh(object):
    def __init__(self, home, away, inning, l_pin, r_pin):
        """

        :type home: MCP23008
        :type away: MCP23008
        :type inning: MCP23008
        """
        # Display objects.
        self.home = home
        self.away = away
        self.inning = inning
        # GPIO pins for switching which segment is on.
        self.left_pin = l_pin
        self.right_pin = r_pin
        # Set up GPIO.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.left_pin, GPIO.OUT)
        GPIO.setup(self.right_pin, GPIO.OUT)

    # Update displays when all numbers are single digit.
    def updateSingle(self):
        # Update each display.
        self.home.writeCache()
        self.away.writeCache()
        self.inning.writeCache()

    # Update displays when at least one is in 2-digit mode.
    def updateDouble(self):
        # Clear all displays.
        self.clear()
        # Switch to left digit.
        GPIO.output(self.right_pin, GPIO.LOW)
        GPIO.output(self.left_pin, GPIO.HIGH)
        # Write the left digit to each display.
        self.write(1)
        # Wait a little while.
        sleep(0.005)
        # Clear again.
        self.clear()
        # Switch to right digit.
        GPIO.output(self.left_pin, GPIO.LOW)
        GPIO.output(self.right_pin, GPIO.HIGH)
        # Write the right digit.
        self.write(2)
        # Wait again...
        sleep(0.005)

    # Clear all displays.
    def clear(self):
        self.home.writeNumber(10)
        self.away.writeNumber(10)
        self.inning.writeNumber(10)

    # Turn off all displays.
    def off(self):
        self.home.off()
        self.away.off()
        self.inning.off()

    # Write to the left or right digit of every display.
    def write(self, digit):
        self.home.writeCache(digit=digit)
        self.away.writeCache(digit=digit)
        self.inning.writeCache(digit=digit)
