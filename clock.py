from luma.core.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from sighandler import SigHandler
from weatherfetcher import WeatherFetcher
from contextlib import contextmanager
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

class TextScroller:
    def __init__(self, text, screenwidth = 20):
        self.text = text
        self.scrolling = False
        self.slicepos = 0
        self.waitcount = 0
        self.extrachars = len(text) - screenwidth if len(text) > screenwidth else 0

    @contextmanager
    def scroll(self, scrolldelay = 3, overscroll = 0):
        if self.slicepos > self.extrachars + overscroll:
            self.slicepos = 0
            self.waitcount = 0
            self.scrolling = False

        yield self.text[self.slicepos:]

        self.waitcount += 1
        if self.extrachars and self.waitcount > scrolldelay:
            self.scrolling = True
            self.slicepos += 1

class ForecastPicker:
    def __init__(self, weatherfetcher):
        self.requests = 0
        self.forecastnum = 0
        self.fetcher = weatherfetcher
        self.default = TextScroller('No forecast data')
        self.current = None
    
    def forecast(self):
        if len(self.fetcher.forecasts):
            self.requests += 1
            if self.current is None or (self.requests > 20 and not self.current.scrolling):
                self.requests = 0
                self.forecastnum = self.forecastnum + 1 if self.forecastnum < 2 else 0
                self.current = TextScroller(self.fetcher.forecasts[self.forecastnum])
            
            return self.current
        return self.default

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

with WeatherFetcher(args.apikey, 300) as weather:
    forecastpicker = ForecastPicker(weather)
    while not sighandler.kill_now:
        if is_between(datetime.now().time(), start, end):
            if not screen_on:
                device.show()
                screen_on = True

            with canvas(device) as draw:
                format = '%H:%M' if not space else '%H %M'
                draw.text((2,2), datetime.now().strftime(format), font=clockfont, fill='white')            
                draw.text((5,40), weather.current, font=infofont, fill='white')  
                with forecastpicker.forecast().scroll(overscroll=3) as text:              
                    draw.text((5,50), text, font=infofont, fill='white')
        else:
            if screen_on:
                device.hide()
                screen_on = False
        
        space = not space
        time.sleep(0.5)

