import threading


# Thread for managing extra info displayed on the LCD screens.
class ExtraInfo(threading.Thread):
    def __init__(self, lcd_ctl):
        threading.Thread.__init__(self)
