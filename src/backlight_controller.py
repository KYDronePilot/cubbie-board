import threading
from Queue import Queue
from time import sleep

import pigpio

PWM_FREQUENCY = 500
UPDATE_DELAY = 0.1


class BacklightController(threading.Thread):
    """
    Controller for LCD display brightness.

    Notes:
        Uses PiGPIO to control PWM of backlight.

    Attributes:
        _pin (int): PWM pin
        _update_queue (Queue): For receiving updates
        _gpio (pigpio.pi): For controlling PWM
        _duty_cycle (int): The current duty cycle
        _stop_handle (threading.Event): Handle to stop the thread

    """

    def __init__(self, pin, gpio):
        # type: (int, pigpio.pi) -> None
        """
        Setup the controller.

        Args:
            pin (int): The PWM pin
            gpio (pigpio.pi): GPIO controller

        """
        threading.Thread.__init__(self)
        self._pin = pin  # type: int
        self._update_queue = Queue()  # type: Queue
        self._gpio = gpio  # type: pigpio.pi
        self._duty_cycle = 0  # type: int
        self._stop_handle = threading.Event()  # type: threading.Event
        # Write initial duty cycle.
        self._write_duty_cycle(self._duty_cycle)

    def _set_duty_cycle(self, duty_cycle):
        # type: (int) -> None
        """
        Manually set the duty cycle.

        Notes:
            Enqueues the duty cycle value.

        Args:
            duty_cycle (int): New duty cycle

        """
        # Ensure duty cycle is within 0 - 100 range.
        if duty_cycle > 100:
            duty_cycle = 100
        elif duty_cycle < 0:
            duty_cycle = 0
        self._update_queue.put(duty_cycle)

    def turn_off(self):
        # type: () -> None
        """
        Turn the display off.

        """
        self._set_duty_cycle(0)

    def turn_on(self):
        # type: () -> None
        """
        Turn the display on (full brightness).

        """
        self._set_duty_cycle(100)

    def stop(self):
        # type: () -> None
        """
        Stop the controller thread.

        """
        self._stop_handle.set()

    def _write_duty_cycle(self, duty_cycle):
        # type: (int) -> None
        """
        Write a duty cycle to the PWM pin.

        Args:
            duty_cycle (int): Duty cycle to write

        """
        self._gpio.hardware_PWM(self._pin, PWM_FREQUENCY, 1e4 * duty_cycle)

    def _transition(self, duty_cycle):
        # type: (int) -> None
        """
        Transition to a new duty cycle through incremental changes.

        Args:
            duty_cycle (int): New duty cycle

        """
        # Exit if already set.
        if duty_cycle == self._duty_cycle:
            return
        # Duty cycle change amount.
        delta = (duty_cycle - self._duty_cycle) / abs(duty_cycle - self._duty_cycle)
        # Change to the new duty cycle.
        while duty_cycle != self._duty_cycle:
            self._duty_cycle += delta
            self._write_duty_cycle(self._duty_cycle)

    def run(self):
        # type: () -> None
        """
        Check for duty cycle changes and make transitions as needed.

        """
        while not self._stop_handle.is_set():
            # If new duty cycle in queue, transition to it.
            if not self._update_queue.empty():
                self._transition(self._update_queue.get())
            # Delay before rechecking.
            sleep(UPDATE_DELAY)
