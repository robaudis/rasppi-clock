import collections

Current = collections.namedtuple('Current', 'temp, summary')
Forecast = collections.namedtuple('Forecast', 'time, forecast')