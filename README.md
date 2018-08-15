# Cubbie Board

![alt text](img/scoreboard_images/IMG_8290.JPG "Cubbie Board Face")

The Cubbie Board is an IOT, Chicago Cubs-themed baseball scoreboard. Powered by a Raspberry Pi Zero W and Python code,
this scoreboard will display your team-of-choice's game when live and cycle through other live MLB games otherwise.


## Parts List

#### Raspberry Pi Zero W
The brains of the Cubbie Board lie in a Raspberry Pi Zero W. For simplicity sake, the [CanaKit 16GB Starter Kit](http://a.co/6ZoiTxW)
is a great all-in-one kit that should have everything needed to get the Pi up and running for this project.

#### LCD Displays
For the LCD displays, 2 [Adafruit 1.44" Color TFT LCD Display with MicroSD Card breakout - ST7735R](https://www.adafruit.com/product/2088)
were used. There are cheaper ST7735R displays that can be found on eBay to lower the final price of the project.

#### 7-Segment Displays
For the 7-segment displays a package of [10, 2 bit, 0.5 inch, cathode displays](http://r.ebay.com/P8kGMW) were 
sourced from eBay. This is by far the cheapest option available.

#### 7-Segment Controllers
For controlling which segments are illuminated on the 7-segment displays, 3 [MCP23008 i2c IO expanders](https://www.adafruit.com/product/593)
from Adafruit are used. There are probably cheaper ways of sourcing these chips, given a few months for shipping.

#### PCB Prototyping Board
Rather than custom designing PCB boards for this project, a pack of [10, 12 x 18 cm prototyping boards](http://r.ebay.com/NOUrGX)
were used. If anyone interested in this project would like to help design a custom PCB, please contact me.

#### Miscellaneous
* Red and Yellow Inning-State LEDs
* 2 P2N2222A NPN Transistors
* 24 [470 Ohm Resistors](http://r.ebay.com/Jjf0el)
* Right Angle Double Row Headers (Probably need fewer than used in this project...)
* [Male to Female Wire Jumpers](http://r.ebay.com/JxYLjP)
* Female 2 x 20 Header for Raspberry Pi
* Soldering equipment
* 8" x 10" Shadow Box
* Scrap Wood (to help mount the Pi and PCB in the shadow box)
* Some resistors for the transistors



## Hardware Configuration
This is a brief overview of how everything works. If you would like to build this project, please contact me and I 
can make schematics.

#### Raspberry Pi
All wiring that needs to connect to the Pi runs to the header pins (of which this build has way too many). From there,
male to female jumpers connect the headers to the Pi.

To make life easier, a female 40-pin header was soldered to the Pi's GPIO rather than using a male header or soldering
each individual wire.

#### LCD Displays
The LCD displays must be controlled through an SPI interface. So the Power, Clock, Slave In, and Data Command pins are
shared between both displays. Each display has its own separate Slave Select, Reset, and Lite (PWM backlight) pins.

#### 7-Segment Displays
Each dual 7-segment display has common anode pins for each segment and 2 separate, common-cathode pins for each digit.
Each segment of each display (minus the dot 'DP' segment) is connected to one of the MCP23008 IO pins via a 
current-limiting 470 ohm resistor. The 8th pin on the right and left MCP23008 expanders is used to power the top and 
bottom inning LEDs, also via 470 ohm resistors. As of now, the middle MCP23008's 8th pin is not being used.

The digit being displayed on each dual 7-segment display is dependent on which common-cathode is pulled low. If both 
are pulled low, both digits will be displayed. To control which digit is being displayed, there are 2 NPN transistors.
The right digits' common-cathodes are connected to the same transistor, as well as the left digits' CC (which introduces 
some software issues). So for basic single digit use, only the right digit transistor is pulled low (see software 
section for info on double digit mode).



## Software Configuration
Once again this is a brief overview of how the code works. For more information, I would recommend reading the inline
comments, as each piece of code is explained there.

#### MLBGame API
All information regarding teams playing and live stats is sourced using the mlbgame Python API created by Panzarino.

#### 7-Segment Displays
Each MCP23008 chip has a low level class that:
* Sets up the chip on init
* Holds the numbers to be displayed on each digit of the segment display
* Keeps track of whether the extra pin (used for inning state on right and left displays) needs to be on
* Displays a number on a specified digit (right or left)

For higher level control, such as changing numbers and inning state, there is a controller thread for managing the 
segments. This thread class has a queue that it occasionally checks for a dict of changes that need to be made.

The controller thread also manages the segment displays' "Double Digit Mode." When one of the numbers being displayed
 is > 9, the controller kicks into Double Digit Mode, blinking the right and left digits on each display on every 
 loop of the main run method.
 
 To make executing mass changes on the segment displays more organized, the direct changes/updates are handled by a
 Refresh class.