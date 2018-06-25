import segment_display
import update_seg_disp
from Queue import Queue
import RPi.GPIO as GPIO

home = segment_display.MCP23008(1, 0x20)
away = segment_display.MCP23008(1, 0x21)
inning = segment_display.MCP23008(1, 0x24)

q = Queue(maxsize=0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

GPIO.output(4, GPIO.HIGH)
GPIO.output(17, GPIO.HIGH)

#update = update_seg_disp.SegmentUpdater(home, None, None, 4, 17, q)
#update.start()

q.put({'home':2}, True)
