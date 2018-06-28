import threading
from Queue import Queue
from time import sleep

PWM_FREQUENCY = 500
UPDATE_DELAY = 0.01


class PWMController(threading.Thread):
    def __init__(self, pin, gpio, current=0):
        threading.Thread.__init__(self)
        # Pin to be controlled.
        self.pin = pin
        # Queue for receiving updates
        self.q = Queue(maxsize=2)
        # PiGPIO object for controlling PWM.
        self.gpio = gpio
        # Handle to shut down the thread.
        self.shut = threading.Event()
        # Lower and upper duty cycle bounds to oscillate between.
        self.lower = 0
        self.upper = 0
        # Whether oscillation needs to increase.
        self.increase = True
        # Current duty cycle.
        self.current = current
        # How fast to dim/brighten.
        self.resolution = 1
        # Write initial duty cycle to the pin.
        self.setPin()

    def run(self):
        while not self.shut.is_set():
            # If nothing in queue, change display brightness appropriately.
            if self.q.empty():
                # Check if current duty cycle needs to be changed.
                if self.lower != self.upper or self.current != self.upper:
                    # If set to increase and current is less than upper, increase.
                    if self.increase and self.current < self.upper:
                        self.current += self.resolution
                    # Same as above, just for decreasing instead.
                    elif not self.increase and self.current > self.lower:
                        self.current -= self.resolution
                    # Update the pin.
                    self.setPin()
                # If upper and lower limits are not same, check if direction of dimming needs to be changed.
                if self.upper != self.lower:
                    # If increasing and near upper limit, or decreasing and near lower limit, reverse.
                    if self.current == self.upper or self.current == self.lower:
                        self.increase = not self.increase
            # Else, something is in queue, let update method handle.
            else:
                self.update()
            # Sleep for designated time before re-checking.
            sleep(UPDATE_DELAY)
        # Before thread ends, be sure to write last duty cycle to pin.
        self.setPin()

    # Separate method for updating the the oscillation info.
    def update(self):
        # Tuple of update data, (lower, upper, boolean force_jump)
        self.lower, self.upper, force_jump = self.q.get()
        # If force_jump set to True, jump to either upper or lower (this implies they are the same).
        if force_jump:
            self.current = self.upper
        # If both the lower and upper bounds are greater than the current value, set to increase.
        if self.lower >= self.current and self.upper >= self.current:
            self.increase = True
        # Elif both bounds are lower than the current, set to decrease.
        elif self.lower <= self.current and self.upper <= self.current:
            self.increase = False
        # Ensure a call is made to update the pin.
        self.setPin()

    # Set PWM pin to current duty cycle.
    def setPin(self):
        self.gpio.hardware_PWM(self.pin, PWM_FREQUENCY, 1e4 * self.current)
