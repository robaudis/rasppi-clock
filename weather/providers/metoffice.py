import requests
import json
from .MetOfficeWeatherTypes import codelist

from datetime import datetime

class MetOfficeProvider():
    def __init__(self, api_key, location):
        self.api_key = api_key
        self.location = location
        self.last_obs_time = ''
        self.current = 'No weather data'

    def fetch(self):
        now = datetime.now().strftime("%Y-%m-%dT%HZ")
        if(now != self.last_obs_time): 
            response = requests.get('http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/{location}?res=hourly&time={time}&key={apikey}'.format(apikey=self.api_key, location=self.location, time=now))
        
            parsed_json = response.json()
            temp_c = parsed_json['SiteRep']['DV']['Location']['Period']['Rep']['T']
            weather_string = codelist[parsed_json['SiteRep']['DV']['Location']['Period']['Rep']['W']]
            self.current = str(temp_c) + u'\u00b0' + " " + weather_string
            self.last_obs_time = now

        return self.current, []

        