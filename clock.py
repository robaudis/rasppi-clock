from luma.core.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from urllib3 import PoolManager
import json
import time
import signal
import os
import threading
import argparse

class SigHandler:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGTERM, self.handler)
    
    def handler(self, signum, frame):
        self.kill_now = True
        
       
class WeatherFetcher(threading.Thread):
    def __init__(self, api_key):
        threading.Thread.__init__(self)
        self.weather = 'No weather data'
        self.api_key = api_key        
        self.running = True if api_key else False        

    def run(self):
        http = PoolManager()
        while self.running:
            r = http.request('GET', 'http://api.wunderground.com/api/%s/geolookup/conditions/q/50.72,-1.98.json' % self.api_key)
            parsed_json = json.loads(r.data.decode('utf-8'))
            temp_c = parsed_json['current_observation']['temp_c']
            weather_string = parsed_json['current_observation']['weather']
            self.weather = str(temp_c) + u"\u00b0" + " " + weather_string
            
            for i in range(0, 900):
                if not self.running: 
                    break
                time.sleep(1)


def in_between(now, start, end):
    if start < end:
        return start <= now < end
    elif end < start:
        return start <= now or now < end
    else:
        return True

parser = argparse.ArgumentParser(description='OLED clock with weather.')
parser.add_argument('--apikey', help='Weather Underground API key.')
args = parser.parse_args()

serial = spi(device=0, port=0)
device = sh1106(serial)

space = False
screen_on = False
path = os.path.dirname(os.path.abspath(__file__))
seglarge = ImageFont.truetype(path + '/fonts/DSEG7Classic-Regular.ttf', 36)
segsmall = ImageFont.truetype(path +'/fonts/ProggyTiny.ttf', 16)
device.contrast(64)
start = datetime.strptime('06:00', '%H:%M').time()
end = datetime.strptime('22:30', '%H:%M').time()

sighandler = SigHandler()

weather = WeatherFetcher(args.apikey)
weather.start()

while not sighandler.kill_now:
    now = datetime.now().time()
    if in_between(now, start, end):
        if not screen_on:
            device.show()
            screen_on = True

        with canvas(device) as draw:
            format = '%H:%M' if not space else '%H %M'
            draw.text((2,2), datetime.now().strftime(format), font=seglarge, fill='white')            
            draw.text((5,40), weather.weather, font=segsmall, fill='white')
            draw.text((5,50), datetime.now().strftime('%d-%m-%Y'), font=segsmall, fill='white')
    else:
        if screen_on:
            device.hide()
            screen_on = False

    space = not space
    time.sleep(0.5)

weather.running = False
weather.join()