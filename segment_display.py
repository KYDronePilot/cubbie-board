# For interfacing with the MCP23008 chip (output only!).

import smbus
from Adafruit_MCP230xx import Adafruit_MCP230XX

# Register to control GPIO pins.
GPIO = 0x09
# Bytes that represent numbers when written to the display.
TRANSLATIONS = {
    0: 0x3F,
    1: 0x06,
    2: 0x5B,
    3: 0x4F,
    4: 0x66,
    5: 0x6D,
    6: 0x7D,
    7: 0x07,
    8: 0x7F,
    9: 0x6F,
    10: 0x00
}


class MCP23008(object):
    def __init__(self, bus_num, i2c_addr):
        self.bus_num = bus_num
        self.i2c_addr = i2c_addr
        # Cached number.
        self.cache_num = 0
        # Cached digits for the left and right display digits.
        self.cache_dig_1 = 10
        self.cache_dig_2 = 0
        # Extra pin state, whether the 8th IO expander pin is set to HIGH or not.
        self.extra_pin_on = False
        # i2c bus to use.
        self.bus = smbus.SMBus(bus_num)
        # Set all MCP23008 pins to output.
        mcp = Adafruit_MCP230XX(busnum=self.bus_num, address=self.i2c_addr, num_gpios=8)
        mcp.config(0, mcp.OUTPUT)
        mcp.config(1, mcp.OUTPUT)
        mcp.config(2, mcp.OUTPUT)
        mcp.config(3, mcp.OUTPUT)
        mcp.config(4, mcp.OUTPUT)
        mcp.config(5, mcp.OUTPUT)
        mcp.config(6, mcp.OUTPUT)
        mcp.config(7, mcp.OUTPUT)

    # Set all IO pins to low on deconstruct.
    def __del__(self):
        self.writeNumber(10)

    # Set certain segments to HIGH.
    def writeHigh(self, pattern):
        # If extra pin is enabled, always ensure the last pin on the MCP23008 will be enabled.
        if self.extra_pin_on:
            pattern += 0x80
        self.bus.write_byte_data(self.i2c_addr, GPIO, pattern)

    # Write a number to the display.
    def writeNumber(self, num):
        self.writeHigh(TRANSLATIONS[num])

    # Update the cached number.
    def updateCache(self, num):
        self.cache_num = num
        self.cache_dig_1 = num // 10
        self.cache_dig_2 = num % 10
        # Don't use left segment if number is zero.
        if self.cache_dig_1 == 0:
            self.cache_dig_1 = 10

    # Write the cached number.
    def writeCache(self, digit=2):
        # Write the correct digit, leaving left digit blank if val is 0.
        if digit == 1 and self.cache_dig_1 != 10:
            self.writeNumber(self.cache_dig_1)
        elif digit == 2:
            self.writeNumber(self.cache_dig_2)
