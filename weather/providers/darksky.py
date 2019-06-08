import requests
import json

from datetime import datetime
from ..providers import Current, Forecast

class DarkSkyProvider():
    def __init__(self, api_key, location):
        self.api_key = api_key
        self.location = location
        self.current = Current('', 'No weather data')
        self.forecasts = []

    def fetch(self):
        response = requests.get('https://api.darksky.net/forecast/{apikey}/{location}?exclude=minutely,daily,alerts,flags&units=uk2'.format(apikey=self.api_key, location=self.location))
    
        parsed_json = response.json()
        temp_c = parsed_json['currently']['temperature']
        weather_string = parsed_json['currently']['summary']
        self.current = Current('{:.1f}{}'.format(temp_c, u'\u00b0'), weather_string)

        del self.forecasts[:]

        for data in parsed_json['hourly']['data']:
            time = datetime.fromtimestamp(int(data['time'])).strftime('%H:%M')
            temp = data['temperature']
            summary = data['summary']
            rain = float(data['precipProbability']) * 100.0
            self.forecasts.append(Forecast('{}:'.format(time), '{:.1f}{} {}, rain: {:.0f}%'.format(temp, u'\u00b0', summary, rain)))   

        return self.current, self.forecasts
