"""
For interfacing with the MCP23008 chip.

"""

import smbus

from decouple import config

from Adafruit_MCP230xx import Adafruit_MCP230XX


class SegmentDisplay(object):
    """
    Interface for controlling a dual, 7-segment display using a MCP23008 chip.

    Attributes:
        i2c_bus (int): I2C bus the chip is connected to
        i2c_addr (int): I2C address of the chip
        _number (int): The number to display
        is_extra_pin_on (bool): Whether the extra pin on the chip is on or off
        bus (smbus.SMBus): The I2C bus
        _digit_1 (int): The first (leftmost) digit to display
        _digit_2 (int): The second (rightmost) digit to display

    """

    # Code for enabling extra pin.
    EXTRA_PIN_CODE = 0x80
    # Register to control GPIO pins.
    GPIO = 0x09
    # Hex codes representing digits on the chip.
    DIGIT_CODES = {
        -1: 0x00,
        0: 0x3F,
        1: 0x06,
        2: 0x5B,
        3: 0x4F,
        4: 0x66,
        5: 0x6D,
        6: 0x7D,
        7: 0x07,
        8: 0x7F,
        9: 0x6F
    }

    def __init__(self, i2c_bus, i2c_addr):
        # type: (int, int) -> None
        """
        Setup the segment display controller chip.
        
        Args:
            i2c_bus (int): I2C bus the chip is connected to
            i2c_addr (int): I2C address of the chip
        
        """
        self._i2c_bus = i2c_bus  # type: int
        self._i2c_addr = i2c_addr  # type: int
        self._number = -1  # type: int
        self.is_extra_pin_on = False  # type: bool
        self.bus = smbus.SMBus(i2c_bus)  # type: smbus.SMBus
        self._digit_1 = -1  # type: int
        self._digit_2 = -1  # type: int
        # Set up chip pins.
        self._setup_pins(i2c_bus, i2c_addr, config('NUM_GPIOS', cast=int))

    @staticmethod
    def _setup_pins(i2c_bus, i2c_addr, num_gpios):
        # type: (int, int, int) -> None
        """
        Setup the chip's GPIO pins.
        
        Notes:
            Sets all pins to output.
        
        Args:
            i2c_bus (int): I2C bus the chip is connected to
            i2c_addr (int): I2C address of the chip
            num_gpios (int): Number of GPIO pins on the chip

        """
        # Create chip controller.
        mcp = Adafruit_MCP230XX(busnum=i2c_bus, address=i2c_addr, num_gpios=num_gpios)
        # Configure each pin for output.
        for i in range(8):
            mcp.config(i, mcp.OUTPUT)

    @property
    def digit_1(self):
        # type: () -> int
        """
        Get the first (leftmost) digit to display.

        Returns:
            int: First digit to display

        """
        return self._digit_1

    @property
    def digit_2(self):
        # type: () -> int
        """
        Get the second (rightmost) digit to display.

        Returns:
            int: Second digit to display

        """
        return self._digit_2

    @property
    def is_double_digit_mode(self):
        # type: () -> bool
        """
        Checks whether the display is in double digit mode.

        Returns:
            bool: Whether the display is in double digit mode

        """
        # If first digit set to some non-negative value, display is in double digit mode.
        return self._digit_1 != -1

    @property
    def number(self):
        # type: () -> int
        """
        Get value for number.

        Returns:
            int: Value of number

        """
        return self._number

    @number.setter
    def number(self, number):
        # type: (int) -> None
        """
        Set a new number value.

        Notes:
            Also calculates and sets new digit values.

        Args:
            number (int): New number value

        """
        self._number = number
        # If default, set both digits accordingly.
        if number == -1:
            self._digit_1 = self._digit_2 = -1
            return
        # Set the first and second digits to display.
        self._digit_1 = (self._number // 10) % 10
        # If only one digit, turn off second digit.
        if self._digit_1 == 0:
            self._digit_1 = -1
        self._digit_2 = self._number % 10

    def _write_code(self, code):
        # type: (int) -> None
        """
        Write a hex code to the chip's pins.
        
        Args:
            code (int): Code to write
        
        """
        # Write to chip.
        self.bus.write_byte_data(self._i2c_addr, SegmentDisplay.GPIO, code)

    def display_digit(self, digit):
        # type: (int) -> None
        """
        Display a digit on one of the 2 segment displays.
        
        Args:
            digit (int): Digit to display
        
        """
        # Encode the digit.
        coded_digit = SegmentDisplay.DIGIT_CODES[digit]
        # Add in extra pin if set to on.
        if self.is_extra_pin_on:
            coded_digit += SegmentDisplay.EXTRA_PIN_CODE
        # Write digit to chip.
        self._write_code(coded_digit)

    def display_digit_1(self):
        # type: () -> None
        """
        Display the first digit.

        """
        self.display_digit(self._digit_1)

    def display_digit_2(self):
        # type: () -> None
        """
        Display the second digit.

        """
        self.display_digit(self._digit_2)

    def off(self):
        # type: () -> None
        """
        Turn off the display.

        """
        # Turn off extra pin.
        self.is_extra_pin_on = False
        # Set to blank number.
        self.number = -1
        # Display a digit.
        self.display_digit_1()
