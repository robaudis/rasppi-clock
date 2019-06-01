from textscroller import TextScroller

class ForecastPicker:
    def __init__(self, weatherfetcher):
        self.requests = 0
        self.forecastnum = 0
        self.fetcher = weatherfetcher
        self.default = TextScroller('No forecast data')
        self.current = None
    
    def forecast(self):
        if len(self.fetcher.forecasts):
            self.requests += 1
            if self.current is None or (self.requests > 20 and not self.current.scrolling):
                self.requests = 0
                self.forecastnum = self.forecastnum + 1 if self.forecastnum < 3 else 0
                self.current = self.fetcher.forecasts[self.forecastnum]
            
            return self.current
        return self.default
