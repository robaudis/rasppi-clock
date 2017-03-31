from urllib3 import PoolManager
import json
import time
import threading


class WeatherFetcher(threading.Thread):
    '''
    Class for fetching weather data every 15mins from Weather Underground
    '''
    def __init__(self, api_key):
        threading.Thread.__init__(self)
        self.current = 'No weather data'
        self.forecast = ['No forecast data', 'No forecast data', 'No forecast data']
        self.api_key = api_key        
        self.running = True if api_key else False        

    def run(self):
        http = PoolManager()
        while self.running:
            r = http.request('GET', 'http://api.wunderground.com/api/%s/conditions/hourly/q/50.72,-1.98.json' % self.api_key)
            parsed_json = json.loads(r.data.decode('utf-8'))
            temp_c = parsed_json['current_observation']['temp_c']
            weather_string = parsed_json['current_observation']['weather']
            self.current = str(temp_c) + u"\u00b0" + " " + weather_string
            
            for i in range(0,3):
                fcasttime = parsed_json['hourly_forecast'][i]['FCTTIME']['hour_padded'] + ':' + parsed_json['hourly_forecast'][i]['FCTTIME']['min']
                fcasttemp = parsed_json['hourly_forecast'][i]
                self.forecast[i] = fcasttime
            
            for i in range(0, 900):
                if not self.running: 
                    break
                time.sleep(1)
