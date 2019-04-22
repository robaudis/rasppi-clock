from .metoffice import MetOfficeProvider

class Factory():
    def __init__(self):
        pass

    def create(self, api_key, location):
        return MetOfficeProvider(api_key, location)