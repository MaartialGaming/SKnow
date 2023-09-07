class SnowCannon:
    def __init__(self, id, broker, port):
        self.id = id
        self.broker = broker
        self.port = port
        self.self = {
            'name': self.id,
            'broker': self.broker,
            'port': self.port,
            'info': {
                    'state': 'off',
                    'mode': 'manual',
                    'auto_value': 100,
                    'prog_time': '00:00-23:59',
                    'water_level': None
                  }
        }

    def setState(self, state):
        self.self['info']['state'] = state

    def setMode(self, mode):
        self.self['info']['mode'] = mode

    def setAutoValue(self, auto_value):
        self.self['info']['auto_value'] = int(auto_value)

    def setProgTime(self, prog_time):
        self.self['info']['prog_time'] = prog_time
    
    def setWaterLevel(self, water_level):
        self.self['info']['water_level'] = int(water_level)

    def getState(self):
        return self.self['info']['state']

    def getInfo(self):
        return self.self['info']
        
    def getSelf(self):
        return self.self