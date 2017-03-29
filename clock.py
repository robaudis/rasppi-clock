from luma.core.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont
from datetime import datetime
import time
import signal
import os

class SigHandler:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGTERM, self.handler)
    
    def handler(self, signum, frame):
        self.kill_now = True

def in_between(now, start, end):
    if start < end:
        return start <= now < end
    elif end < start:
        return start <= now or now < end
    else:
        return True

serial = spi(device=0, port=0)
device = sh1106(serial)

space = False
screen_on = False
path = os.path.dirname(os.path.abspath(__file__))
seglarge = ImageFont.truetype(path + '/fonts/DSEG7Classic-Regular.ttf', 36)
segsmall = ImageFont.truetype(path +'/fonts/DSEG7Classic-Regular.ttf', 14)
device.contrast(64)
start = datetime.strptime('06:00', '%H:%M').time()
end = datetime.strptime('22:00', '%H:%M').time()

sighandler = SigHandler()

while not sighandler.kill_now:
    now = datetime.now().time()
    if in_between(now, start, end):
        if not screen_on:
            device.show()
            screen_on = True

        with canvas(device) as draw:
            format = '%H:%M' if not space else '%H %M'
            draw.text((2,2), datetime.now().strftime(format), font=seglarge, fill='white')
            draw.text((10,45), datetime.now().strftime('%d-%m-%Y'), font=segsmall, fill='white')
    else:
        if screen_on:
            device.hide()
            screen_on = False

    space = not space
    time.sleep(0.5)
