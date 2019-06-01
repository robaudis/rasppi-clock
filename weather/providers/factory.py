from .metoffice import MetOfficeProvider
from .darksky import DarkSkyProvider
from .null import NullProvider

class Factory():
    def __init__(self):
        pass

    def create(self, provider, api_key, location):
        if provider == 'darksky':
            return DarkSkyProvider(api_key, location)
        elif provider == 'metoffice':
            return MetOfficeProvider(api_key,location)
        else:
            return NullProvider()