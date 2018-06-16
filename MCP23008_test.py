from Adafruit_MCP230xx import Adafruit_MCP230XX
import time

# ***************************************************
# Set num_gpios to 8 for MCP23008 or 16 for MCP23017!
# ***************************************************
mcp = Adafruit_MCP230XX(busnum = 1, address = 0x20, num_gpios = 8) # MCP23008
# mcp = Adafruit_MCP230XX(address = 0x20, num_gpios = 16) # MCP23017

# Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
mcp.config(0, mcp.OUTPUT)
mcp.config(1, mcp.OUTPUT)
mcp.config(2, mcp.OUTPUT)
mcp.config(3, mcp.OUTPUT)
mcp.config(4, mcp.OUTPUT)
mcp.config(5, mcp.OUTPUT)
mcp.config(6, mcp.OUTPUT)
mcp.config(7, mcp.OUTPUT)

# Set pin 3 to input with the pullup resistor enabled
#mcp.config(3, mcp.INPUT)
#mcp.pullup(3, 1)

# Read input pin and display the results
#print "Pin 3 = %d" % (mcp.input(3) >> 3)

# Python speed test on output 0 toggling at max speed
print "Starting blinky on pin 0 (CTRL+C to quit)"
while (True):
  mcp.output(0, 1)  # Pin 0 (segment A) High
  mcp.output(1, 1)  # Pin 1 (segment B) High
  mcp.output(2, 1)  # Pin 2 (segment C) High
  mcp.output(3, 1)  # Pin 3 (segment D) High
  mcp.output(4, 1)  # Pin 4 (segment E) High
  mcp.output(5, 1)  # Pin 5 (segment F) High
  mcp.output(6, 1)  # Pin 6 (segment G) High
  mcp.output(7, 1)  # Pin 7 (segment DP) High
  #time.sleep(0.01667);
  mcp.output(0, 0)  # Pin 0 Low
  mcp.output(1, 0)  # Pin 1 Low
  mcp.output(2, 0)  # Pin 2 Low
  mcp.output(3, 0)  # Pin 3 Low
  mcp.output(4, 0)  # Pin 4 Low
  mcp.output(5, 0)  # Pin 5 Low
  mcp.output(6, 0)  # Pin 6 Low
  mcp.output(7, 0)  # Pin 7 Low
  #time.sleep(0.01667);


# Use busnum = 0 for older Raspberry Pi's (256MB)
mcp = Adafruit_MCP230XX(busnum = 0, address = 0x20, num_gpios = 16)
# Use busnum = 1 for new Raspberry Pi's (512MB with mounting holes)
# mcp = Adafruit_MCP230XX(busnum = 1, address = 0x20, num_gpios = 16)

# Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
mcp.config(0, OUTPUT)
mcp.config(1, OUTPUT)
mcp.config(2, OUTPUT)

# Set pin 3 to input with the pullup resistor enabled
mcp.pullup(3, 1)
# Read pin 3 and display the results
print "%d: %x" % (3, mcp.input(3) >> 3)

# Python speed test on output 0 toggling at max speed
mcp.output(5, 1)  # Pin 0 High
