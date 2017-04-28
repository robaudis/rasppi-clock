import requests
import json
import time
import threading


class WeatherFetcher(threading.Thread):
    '''
    Class for fetching weather data every x seconds from Weather Underground
    '''
    def __init__(self, api_key, interval = 900):
        threading.Thread.__init__(self)
        self.current = 'No weather data'
        self.forecasts = []
        self.api_key = api_key   
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
                r = requests.get('http://api.wunderground.com/api/%s/conditions/hourly/q/50.72,-1.98.json' % self.api_key)
                parsed_json = r.json()
                temp_c = parsed_json['current_observation']['temp_c']
                weather_string = parsed_json['current_observation']['weather']
                self.current = str(temp_c) + u'\u00b0' + " " + weather_string
            
                del self.forecasts[:]
                for fcast in parsed_json['hourly_forecast']:
                    fcasttime = fcast['FCTTIME']['hour_padded'] + ':' + fcast['FCTTIME']['min']
                    fcasttemp = fcast['temp']['metric'] + u'\u00b0'
                    fcastcondition = fcast['condition']
                    self.forecasts.append('{}: {} {}'.format(fcasttime, fcasttemp, fcastcondition))
            except (requests.exceptions.RequestException, ValueError):
                self.current = 'Unable to fetch data'
                del self.forecasts[:]

            for i in range(0, self.interval):
                if not self.running: 
                    break
                time.sleep(1)
