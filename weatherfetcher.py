import requests
import json
import time
import threading
import logging

from datetime import datetime
from textscroller import TextScroller

logging.basicConfig(filename='piclock.log',level=logging.INFO)
class WeatherFetcher(threading.Thread):
    '''
    Class for fetching weather data every x seconds from a weather provider
    '''
    def __init__(self, provider, interval = 900):
        threading.Thread.__init__(self)
        self.provider = provider
        self.current = 'No weather data'
        self.forecasts = [] 
        self.interval = interval
        self.running = True if provider else False        
    
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, type, value, traceback):
        self.running = False
        self.join()
        return False
    
    def run(self):
        while self.running:
            try:
                self.current, forecasts = self.provider.fetch()
                self.forecasts = [TextScroller(forecast) for forecast in forecasts]

            except (requests.exceptions.RequestException, ValueError) as e:
                logging.error(str(e))

            for _ in range(0, self.interval):
                if not self.running: 
                    break
                time.sleep(1)
