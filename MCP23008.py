# For interfacing with the MCP23008 chip (output only!).

import smbus

# Register to control GPIO pins.
GPIO = 0x09

class MCP23008(object):
    def __init__(self, bus_num, i2c_addr):
        self.bus_num = bus_num
        self.i2c_addr - i2c_addr
        self.bus = smbus.SMBus(bus_num)
    
    # Set certain segments to HIGH.
    def writeHigh(self, pattern):
        bus.write_byte_data(self.i2c_addr, GPIO, pattern)