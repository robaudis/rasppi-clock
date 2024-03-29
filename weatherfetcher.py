import requests
import json
import time
import threading
import logging

from datetime import datetime
from textscroller import TextScroller

class WeatherFetcher(threading.Thread):
    '''
    Class for fetching weather data every x seconds from a weather provider
    '''
    def __init__(self, provider, interval = 900):
        threading.Thread.__init__(self)
        self.provider = provider
        self.current = TextScroller('', 'No weather data')
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
                current, forecasts = self.provider.fetch()
                self.current = TextScroller(current.temp, current.summary)
                self.forecasts = [TextScroller(forecast.time, forecast.forecast) for forecast in forecasts]

            except (requests.exceptions.ConnectionError, requests.exceptions.RequestException, ValueError) as e:
                pass

            for _ in range(0, self.interval):
                if not self.running: 
                    break
                time.sleep(1)
