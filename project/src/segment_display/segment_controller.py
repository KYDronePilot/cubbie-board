"""
Module for managing the 7-segment displays.

"""

import threading
from Queue import Queue
from time import sleep

import RPi.GPIO as GPIO
from decouple import config
from typing import Union, Dict, Tuple, Callable

from .segment_display import SegmentDisplay


class SegmentController(threading.Thread):
    """
    Threaded controller for the 7-segment displays.

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

    # Timeout between blinking digits.
    BLINK_TIMEOUT = 0.005

    def __init__(self):
        # type: () -> None
        """
        Construct the segment display controller.

        """
        threading.Thread.__init__(self)
        # Construct the segment displays.
        self.home_display = SegmentDisplay(
            1, int(config('HOME_MCP23008_ADDRESS'), 0)
        )  # type: SegmentDisplay
        self.away_display = SegmentDisplay(
            1, int(config('AWAY_MCP23008_ADDRESS'), 0)
        )  # type: SegmentDisplay
        self.inning_display = SegmentDisplay(
            1, int(config('INNING_MCP23008_ADDRESS'), 0)
        )  # type: SegmentDisplay
        self._left_digit_pin = config('LEFT_DIGIT_PIN', cast=int)  # type: int
        self._right_digit_pin = config('RIGHT_DIGIT_PIN', cast=int)  # type: int
        self._update_queue = Queue()  # type: Queue
        self._stop_handle = threading.Event()  # type: threading.Event
        self._is_double_mode = False  # type: bool
        self._is_top_inning = True  # type: bool
        self._update_functions = {
            'inning': self.update_inning,
            'inning_state': self.update_inning_state,
            'home_team_runs': self.update_home_score,
            'away_team_runs': self.update_away_score
        }  # type: Dict[str, Callable]
        # Set up digit pins.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._left_digit_pin, GPIO.OUT)
        GPIO.setup(self._right_digit_pin, GPIO.OUT)
        # Initially set to display the right digit.
        GPIO.output(self._left_digit_pin, GPIO.LOW)
        GPIO.output(self._right_digit_pin, GPIO.HIGH)

    def update_inning(self, inning):
        # type: (int) -> None
        """
        Update the inning display with a new number.

        Args:
            inning (int): New inning

        Returns:
            None

        """
        self.inning_display.number = inning

    def update_inning_state(self, state):
        # type: (str) -> None
        """
        Update the inning state.

        Notes:
            Home display's extra pin is connected to the top inning indicator, away display's is connected to
            the bottom inning indicator.

        Args:
            state (str): Inning state (one of 'Top' or 'Bottom')

        Returns:
            None

        """
        # If top, enable top indicator.
        if state == 'Top':
            self.home_display.is_extra_pin_on = True
            self.away_display.is_extra_pin_on = False
        # If bottom, enable bottom indicator.
        elif state == 'Bottom':
            self.home_display.is_extra_pin_on = False
            self.away_display.is_extra_pin_on = True
        # Else, turn off indicators.
        else:
            self.home_display.is_extra_pin_on = False
            self.away_display.is_extra_pin_on = False

    def update_home_score(self, home_score):
        # type: (int) -> None
        """
        Update the home display with a new score.

        Args:
            home_score (int): New score

        Returns:
            None

        """
        self.home_display.number = home_score

    def update_away_score(self, away_score):
        # type: (int) -> None
        """
        Update the away display with a new score.

        Args:
            away_score (int): New score

        Returns:
            None

        """
        self.away_display.number = away_score

    def _update_display_mode(self):
        # type: () -> None
        """
        Update whether the display is in single or double digit mode.

        Returns:
            None

        """
        # System is in double digit mode if only one display is.
        if (
                self.home_display.is_double_digit_mode
                or self.away_display.is_double_digit_mode
                or self.inning_display.is_double_digit_mode
        ):
            self._is_double_mode = True
        else:
            self._is_double_mode = False

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

        Returns:
            None

        """
        self._update_queue.put((key, value))

    def process_update(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Process an update taken from the queue.

        Notes:
            Passes the key and value to the function needed to process them.

        Args:
            key (str): Field name
            value (Union[str, int]): Update value

        Returns:
            None

        """
        # Get the function handler.
        handler = self._update_functions[key]
        # Execute it.
        handler(value)
        # Update the display mode.
        self._update_display_mode()

    def process_updates(self):
        # type: () -> None
        """
        Read and process all updates on the update queue.

        Returns:
            None

        """
        while not self._update_queue.empty():
            update_item = self._read_update()
            self.process_update(update_item[0], update_item[1])
        # If not in double digit mode, display second digit on each display.
        if not self._is_double_mode:
            self._display_digit_2()

    def _display_digit_1(self):
        # type: () -> None
        """
        Display the first digit on each display.

        Returns:
            None

        """
        self.home_display.display_digit_1()
        self.away_display.display_digit_1()
        self.inning_display.display_digit_1()

    def _display_digit_2(self):
        # type: () -> None
        """
        Display the second digit on each display.

        Returns:
            None

        """
        self.home_display.display_digit_2()
        self.away_display.display_digit_2()
        self.inning_display.display_digit_2()

    def _clear(self):
        # type: () -> None
        """
        Quickly clear the display.

        Returns:
            None

        """
        self.home_display.display_digit(-1)
        self.away_display.display_digit(-1)
        self.inning_display.display_digit(-1)

    def _blink_digits(self):
        # type: () -> None
        """
        Blink each digit on each display.

        Returns:
            None

        """
        # Clear displays.
        self._clear()
        # Switch to lighting left digit.
        GPIO.output(self._right_digit_pin, GPIO.LOW)
        GPIO.output(self._left_digit_pin, GPIO.HIGH)
        # Display digit 1 on each display.
        self._display_digit_1()
        sleep(SegmentController.BLINK_TIMEOUT)
        # Clear again.
        self._clear()
        # Switch to lighting right digit.
        GPIO.output(self._left_digit_pin, GPIO.LOW)
        GPIO.output(self._right_digit_pin, GPIO.HIGH)
        # Display digit 2 on each display.
        self._display_digit_2()
        sleep(SegmentController.BLINK_TIMEOUT)

    def exit(self):
        # type: () -> None
        """
        Prepare display for script exit.

        Returns:
            None

        """
        # Stop the thread.
        self._stop_handle.set()
        # Join thread.
        self.join()
        # Cleanup GPIO and shut off displays.
        GPIO.cleanup()
        self.home_display.off()
        self.away_display.off()
        self.inning_display.off()

    def run(self):
        # type: () -> None
        """
        Main thread execution function.

        Notes:
            Continue updating the display until stop handle is set.

        Returns:
            None

        """
        while not self._stop_handle.is_set():
            # If there are updates, process them.
            if not self._update_queue.empty():
                self.process_updates()
            # If in double digit mode, blink digits.
            if self._is_double_mode:
                self._blink_digits()
            # Delay some amount of time.
            sleep(0.01)
