class NullProvider():
    def __init__(self):
        self.current = 'No provider selected'
        self.forecasts = []

    def fetch(self):
        return self.current, self.forecasts