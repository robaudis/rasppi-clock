from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont

from datetime import datetime

from sighandler import SigHandler
from weatherfetcher import WeatherFetcher
from forecastpicker import ForecastPicker

import time
import os
import argparse
import json
from weather.providers.factory import Factory

from pathlib import Path

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

#parser = argparse.ArgumentParser(description='OLED clock with weather.')
#parser.add_argument('--apikey', help='Weather Provider API key.', required=True)
#parser.add_argument('--location', help='Location', required=True)
#parser.add_argument('--provider', help='Provider [metoffice|darksky|openweathermap]', required=False)
#args = parser.parse_args()

p = Path(__file__).with_name('config.json')
#configfile = p.absolute()

with p.open('r') as f:
    args = json.load(f)

serial = spi(device=0, port=0)
device = sh1106(serial)
device.contrast(128)

space = False
screen_on = False

clockfont = make_font('DSEG7Classic-Regular', 36)
infofont = make_font('ProggyTiny', 16)

start = datetime.strptime('06:00', '%H:%M').time()
end = datetime.strptime('23:30', '%H:%M').time()

sighandler = SigHandler()

provider = Factory().create(args["provider"], args["apikey"], args["location"])

with WeatherFetcher(provider, 300) as weather:
    forecastpicker = ForecastPicker(weather)
    while not sighandler.kill_now:
        if is_between(datetime.now().time(), start, end):
            if not screen_on:
                device.show()
                screen_on = True

            with canvas(device) as draw:
                format = '%H:%M' if not space else '%H %M'
                draw.text((2,2), datetime.now().strftime(format), font=clockfont, fill='white')   
                with weather.current.scroll(overscroll=3) as current:
                    draw.text((5,40), current, font=infofont, fill='white')  
                with forecastpicker.forecast().scroll(overscroll=3) as text:              
                    draw.text((5,50), text, font=infofont, fill='white')
        else:
            if screen_on:
                device.hide()
                screen_on = False
        
        space = not space
        time.sleep(0.5)

