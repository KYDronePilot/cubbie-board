import segment_display
import update_seg_disp
from Queue import Queue

home = segment_display.MCP23008(1, 0x20)
away = segment_display.MCP23008(1, 0x22)
inning = segment_display.MCP23008(1, 0x24)

q = Queue(maxsize=0)

update = update_seg_disp.Updater(home, away, inning, 4, 17, q)
update.start()

q.put({'home':2}, True)
