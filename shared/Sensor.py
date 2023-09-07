import random
import datetime
class Sensor:
    def __init__(self, id, broker, port, type, unit):
        self.id = id
        self.broker = broker
        self.port = port
        self.type = type
        self.unit = unit
        self.self = {
            'name': self.id,
            'broker': self.broker,
            'port': self.port,
            'info': {
                    'type': self.type,
                    'unit': self.unit
                  }
        }
        self.prev_measurement = None

    def getMeasurement(self):
        pass

    def getSelf(self):
        return self.self

class SnowDepthSensor(Sensor):
    def __init__(self, id, broker, port, type, unit):
        super().__init__(id, broker, port, type, unit)
        self.prev_measurement = random.randint(0, 1000)

    def getMeasurement(self):
        measurement = {}
        measurement['type'] = self.self['info']['type']
        measurement['unit'] = self.self['info']['unit']
        measurement['value'] = max(0, int(self.prev_measurement + random.randint(-50, 50)))
        self.prev_measurement = measurement['value']
        measurement['timestamp'] = datetime.datetime.now().strftime('%Y/%m/%d, %H:%M:%S')
        return measurement

class TemperatureSensor(Sensor):
    def __init__(self, id, broker, port, type, unit):
        super().__init__(id, broker, port, type, unit)
        self.prev_measurement = random.randint(-10, 5)

    def getMeasurement(self):
        measurement = {}
        measurement['type'] = self.self['info']['type']
        measurement['unit'] = self.self['info']['unit']
        measurement['value'] = round(self.prev_measurement + random.random() - 0.5, 1)
        self.prev_measurement = measurement['value']
        measurement['timestamp'] = datetime.datetime.now().strftime('%Y/%m/%d, %H:%M:%S')
        return measurement

class HumiditySensor(Sensor):
    def __init__(self, id, broker, port, type, unit):
        super().__init__(id, broker, port, type, unit)
        self.prev_measurement = random.randint(40, 60)

    def getMeasurement(self):
        measurement = {}
        measurement['type'] = self.self['info']['type']
        measurement['unit'] = self.self['info']['unit']
        measurement['value'] = max(0, min(100, int(self.prev_measurement + random.randint(-2, 2))))
        self.prev_measurement = measurement['value']
        measurement['timestamp'] = datetime.datetime.now().strftime('%Y/%m/%d, %H:%M:%S')
        return measurement

class WaterLevelSensor(Sensor):
    def __init__(self, id, broker, port, type, unit):
        super().__init__(id, broker, port, type, unit)
        self.prev_measurement = random.randint(90, 100)

    def getMeasurement(self):
        measurement = {}
        measurement['type'] = self.self['info']['type']
        measurement['unit'] = self.self['info']['unit']
        if random.random() <= self.prev_measurement / 100:
            measurement['value'] = max(0, self.prev_measurement - random.randint(15, 20))
        else:
            measurement['value'] = random.randint(90, 100)
        self.prev_measurement = measurement['value']
        measurement['timestamp'] = datetime.datetime.now().strftime('%Y/%m/%d, %H:%M:%S')
        return measurement