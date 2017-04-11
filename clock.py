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

class ForecastPicker:
    def __init__(self, weatherfetcher):
        self.requests = 0
        self.forecastnum = 0
        self.fetcher = weatherfetcher
    
    def forecast(self):
        if len(self.fetcher.forecasts):
            self.requests += 1
            if self.requests > 20:
                self.requests = 0
                self.forecastnum = self.forecastnum + 1 if self.forecastnum < 2 else 0
            
            return self.fetcher.forecasts[self.forecastnum]
        return 'No forecast data'

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

slicepos = 0
extrachars = 0
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
                #draw.text((5,50), datetime.now().strftime('%d-%m-%Y'), font=infofont, fill='white')
                forecast = forecastpicker.forecast()
                length = len(forecast)
                
                extrachars = length - 20 if length - 20 else zero
                draw.text((5,50), forecast[slicepos:], font=infofont, fill='white')
        else:
            if screen_on:
                device.hide()
                screen_on = False
        
        slicepos += 1
        if slicepos > extrachars:
            slicepos = 0
        space = not space
        time.sleep(0.5)

