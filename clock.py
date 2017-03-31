from luma.core.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from sighandler import SigHandler
from weatherfetcher import WeatherFetcher
import time
import os
import argparse

              
def is_between(now, start, end):
    if start < end:
        return start <= now < end
    elif end < start:
        return start <= now or now < end
    else:
        return True
        
def make_font(fontname, size):
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    return ImageFont.truetype(os.path.join(scriptpath, 'fonts', '%s.ttf' % fontname), size)
        
parser = argparse.ArgumentParser(description='OLED clock with weather.')
parser.add_argument('--apikey', help='Weather Underground API key.')
args = parser.parse_args()

serial = spi(device=0, port=0)
device = sh1106(serial)
device.contrast(64)

space = False
screen_on = False

clockfont = make_font('DSEG7Classic-Regular', 36)
infofont = make_font('ProggyTiny', 16)

start = datetime.strptime('06:00', '%H:%M').time()
end = datetime.strptime('22:30', '%H:%M').time()

sighandler = SigHandler()

weather = WeatherFetcher(args.apikey)
weather.start()

while not sighandler.kill_now:
    if is_between(datetime.now().time(), start, end):
        if not screen_on:
            device.show()
            screen_on = True

        with canvas(device) as draw:
            format = '%H:%M' if not space else '%H %M'
            draw.text((2,2), datetime.now().strftime(format), font=clockfont, fill='white')            
            draw.text((5,40), weather.current, font=infofont, fill='white')
            draw.text((5,50), datetime.now().strftime('%d-%m-%Y'), font=infofont, fill='white')
            #draw.text((5,50), weather.forecast[0], font=infofont, fill='white')
    else:
        if screen_on:
            device.hide()
            screen_on = False

    space = not space
    time.sleep(0.5)

weather.running = False
weather.join()
