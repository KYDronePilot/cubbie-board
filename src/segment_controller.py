"""
Module for managing the 7-segment displays.

"""

import threading
from Queue import Queue
from time import sleep

import RPi.GPIO as GPIO

from segment_display import SegmentDisplay
from decouple import config
from typing import List, Union, Dict, Tuple, Any, Callable

# Number of iterations before checking the queue.
COUNTER = 100


# Main worker function that watches for digit changes, applying as needed and
# blinks the segments if in 2-segment mode.
class SegmentController(threading.Thread):
    """
    Threaded controller for the 7-segment displays.

    Notes:
        TODO: Add thread-safe attribute to functions that are.

    Attributes:
        home_display (SegmentDisplay): Home display
        away_display (SegmentDisplay): Away display
        inning_display (SegmentDisplay): Inning display
        _left_digit_pin (int): Pin for enabling the left digit
        _right_digit_pin (int): Pin for enabling the right digit
        _update_queue (Queue): For receiving updates
        _stop_handle (threading.Event): Handle to stop the thread
        _is_double_mode (bool): Whether the display is in double digit mode
        _is_top_inning (bool): Whether or not it is the top of the inning
        _update_functions (Dict[str, Callable]): Functions for handling updates of specific fields

    """

    def __init__(self, _left_digit_pin, _right_digit_pin):
        """
        Construct the segment display controller.

        Args:
            _left_digit_pin (int): Pin for enabling the left digit
            _right_digit_pin (int): Pin for enabling the right digit

        """
        threading.Thread.__init__(self)
        # Construct the segment displays.
        self.home_display = SegmentDisplay(
            1, config('HOME_MCP23008_ADDRESS', cast=int)
        )  # type: SegmentDisplay
        self.away_display = SegmentDisplay(
            1, config('AWAY_MCP23008_ADDRESS', cast=int)
        )  # type: SegmentDisplay
        self.inning_display = SegmentDisplay(
            1, config('INNING_MCP23008_ADDRESS', cast=int)
        )  # type: SegmentDisplay
        self._left_digit_pin = _left_digit_pin  # type: int
        self._right_digit_pin = _right_digit_pin  # type: int
        self._update_queue = Queue()  # type: Queue
        self._stop_handle = threading.Event()  # type: threading.Event
        self._is_double_mode = False  # type: bool
        self._is_top_inning = True  # type: bool
        # Initial set to the right digit.
        GPIO.output(left_dig_tran, GPIO.LOW)
        GPIO.output(right_dig_tran, GPIO.HIGH)
        # Counter for determining if the queue should be checked.
        self.cnt = COUNTER
        # For keeping track of whether the display should be on or off.
        self.on = False
        self._update_functions = {
            'inning': self.update_inning,
            'inning_state': self.update_inning_state,
            'home_team_runs': self.update_home_score,
            'away_team_runs': self.update_away_score
        }  # type: Dict[str, Callable]

    def update_inning(self, inning):
        # type: (int) -> None
        """
        Update the inning display with a new number.

        Args:
            inning (int): New inning

        """
        self.inning_display.number = inning

    def update_inning_state(self, state):
        # type: (str) -> None
        """
        Update the inning state.

        Notes:
            Home display's extra pin is connected to the top of inning indicator, away display's is connected to
            the bottom of inning indicator.

        Args:
            state (str): Inning state (one of 'Top' or 'Bottom')

        """
        if state == 'Top':
            self.home_display.is_extra_pin_on = True
            self.away_display.is_extra_pin_on = False
        if state == 'Bottom':
            self.home_display.is_extra_pin_on = False
            self.away_display.is_extra_pin_on = True
        else:
            # Else, turn off indicators.
            self.home_display.is_extra_pin_on = False
            self.away_display.is_extra_pin_on = False

    def update_home_score(self, home_score):
        # type: (int) -> None
        """
        Update the home display with a new score.

        Args:
            home_score (int): New score

        """
        self.home_display.number = home_score

    def update_away_score(self, away_score):
        # type: (int) -> None
        """
        Update the away display with a new score.

        Args:
            away_score (int): New score

        """
        self.away_display.number = away_score

    def _read_update(self):
        # type: () -> Union[Tuple[str, Union[str, int]], None]
        """
        Read and return an update from the update queue.

        Returns:
            Union[Tuple[str, Union[str, int]], None]: Next item on the update queue

        """
        # Return nothing if no items in queue.
        if self._update_queue.empty():
            return None
        item = self._update_queue.get()
        return item[0], item[1]

    def write_update(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Write an update to the update queue.

        Notes:
            Thread-safe

        Args:
            key (str): Field name
            value (Union[str, int]): Update value

        """
        self._update_queue.put((key, value))

    def process_update(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Process an update taken from the queue.

        Notes:
            Passes the key and value to the function needed to process them.

        Args:
            key (str): Key describing update
            value (Union[str, int]): Update value

        """
        # Get the function handler.
        handler = self._update_functions[key]
        # Execute it.
        handler(value)

    # Cleanup the GPIO and shut off the displays on delete.
    def __del__(self):
        GPIO.cleanup()
        self.refresh.off()

    # Actual thread that is run.
    def run(self):
        while not self._stop_handle.is_set():
            # Wait a little bit before checking the counter.
            sleep(0.002)
            # Call cache updater method if counter has reached 0.
            if self.cnt == 0:
                self.update_cache()
            # If not in single digit mode and displays are on, blink both digits on each display.
            elif not self._is_double_mode and self.on:
                self.refresh.update_double()
            # Decrement the counter.
            self.cnt -= 1

    # Update the segment display caches if there is something in the queue.
    def update_cache(self):
        # Reset counter.
        self.cnt = COUNTER
        # Exit if the queue is empty.
        if self.q.empty():
            return
        # Initially set that the displays will be on.
        self.on = True
        # Get dictionary of updated values.
        val_dict = self.q.get()
        for key, val in val_dict.items():
            # Update display objects if name and val in the dict.
            if key == 'home_team_runs':
                self.refresh.home.update_cache(val)
            elif key == 'away_team_runs':
                self.refresh.away.update_cache(val)
            elif key == 'inning':
                self.refresh.inning.update_cache(val)
            elif key == 'inning_state':
                # Home display's extra IO pin represents top, away's represents bottom.
                if val == 'Top':
                    self.refresh.home.is_extra_pin_on = True
                    self.refresh.away.is_extra_pin_on = False
                elif val == 'Bottom':
                    self.refresh.home.is_extra_pin_on = False
                    self.refresh.away.is_extra_pin_on = True
            # Shut off all displays.
            elif key == 'off':
                self.refresh.off()
                # Set that the displays are off.
                self.on = False
        # After updating the values, set to the correct segment mode.
        self.check_mode()
        # Only run an update method if the displays are on.
        if self.on:
            # Update the display using single mode.
            if self._is_double_mode:
                self.refresh.update_single()
            # Update the display using double mode.
            else:
                self.refresh.update_double()

    # Checks current display numbers to determine whether to be in single mode or not.
    def check_mode(self):
        # If all displays' left digits are blank, set to single mode.
        if (
                self.refresh.home.cache_dig_1 == 10 and
                self.refresh.away.cache_dig_1 == 10 and
                self.refresh.inning.cache_dig_1 == 10
        ):
            self._is_double_mode = True
        # Else, set to 2-segment mode.
        else:
            self._is_double_mode = False


# Handles refreshing of the displays.
class Refresh(object):
    def __init__(self, home, away, inning, l_pin, r_pin):
        """

        :type home: SegmentDisplay
        :type away: SegmentDisplay
        :type inning: SegmentDisplay
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
    def update_single(self):
        # Update each display.
        self.home.write_cache()
        self.away.write_cache()
        self.inning.write_cache()

    # Update displays when at least one is in 2-digit mode.
    def update_double(self):
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
        self.home.write_number(10)
        self.away.write_number(10)
        self.inning.write_number(10)

    # Turn off all displays.
    def off(self):
        self.home.off()
        self.away.off()
        self.inning.off()

    # Write to the left or right digit of every display.
    def write(self, digit):
        self.home.write_cache(digit=digit)
        self.away.write_cache(digit=digit)
        self.inning.write_cache(digit=digit)
