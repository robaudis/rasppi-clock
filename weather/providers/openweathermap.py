import requests
import json

from datetime import datetime
from ..providers import Current, Forecast

class OpenWeatherMapProvider():
    def __init__(self, api_key, location):
        self.api_key = api_key
        self.location = location
        self.current = Current('', 'No weather data')
        self.forecasts = []
        self.gotlocation = False
        self.lat = 200
        self.lon = 200        

    def _init_location(self):
        response = requests.get('http://api.openweathermap.org/geo/1.0/zip?zip={zip}&appid={apikey}'.format(apikey=self.api_key, zip=self.location))
        parsed = response.json()
        self.lat = parsed['lat']
        self.lon = parsed['lon']
        self.gotlocation = True

    def fetch(self):

        if not self.gotlocation:
            self._init_location()
        
        response = requests.get('https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,daily,alerts&units=metric&appid={apikey}'.format(apikey=self.api_key, lat=self.lat, lon=self.lon))
    
        parsed_json = response.json()
        temp_c = parsed_json['current']['temp']
        weather_string = parsed_json['current']['weather'][0]['description']
        self.current = Current('{:.1f}{}'.format(temp_c, u'\u00b0'), weather_string)

        del self.forecasts[:]

        for data in parsed_json['hourly']:
            time = datetime.fromtimestamp(int(data['dt'])).strftime('%H:%M')
            temp = data['temp']
            summary = data['weather'][0]['description']
            rain = float(data['pop']) * 100.0
            self.forecasts.append(Forecast('{}:'.format(time), '{:.1f}{} {}, rain: {:.0f}%'.format(temp, u'\u00b0', summary, rain)))   

        return self.current, self.forecasts
