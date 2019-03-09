import requests
import json
import time
import threading
import logging
import weathertypes

from datetime import datetime
from textscroller import TextScroller

logging.basicConfig(filename='piclock.log',level=logging.INFO)
class WeatherFetcher(threading.Thread):
    '''
    Class for fetching weather data every x seconds from Met Office Datapoint
    '''
    def __init__(self, api_key, location, interval = 900):
        threading.Thread.__init__(self)
        self.last_obs_time = ''
        self.current = 'No weather data'
        self.forecasts = []
        self.api_key = api_key
        self.location = location   
        self.interval = interval
        self.running = True if api_key else False        
    
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
                now = datetime.now().strftime("%Y-%m-%dT%HZ")
                if(now != self.last_obs_time): 
                    response = requests.get('http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/{location}?res=hourly&time={time}&key={apikey}'.format(apikey=self.api_key, location=self.location, time=now))
               
                    parsed_json = response.json()
                    temp_c = parsed_json['SiteRep']['DV']['Location']['Period']['Rep']['T']
                    weather_string = weathertypes.codelist[parsed_json['SiteRep']['DV']['Location']['Period']['Rep']['W']]
                    self.current = str(temp_c) + u'\u00b0' + " " + weather_string
                    self.last_obs_time = now
            except (requests.exceptions.RequestException, ValueError) as e:
                logging.error(str(e))

            for i in range(0, self.interval):
                if not self.running: 
                    break
                time.sleep(1)
