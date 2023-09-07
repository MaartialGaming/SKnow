#!/usr/bin/env python

import sys
import os
import requests
import json
import time
sys.path.append('/shared')
from MQTTClient import MQTTClient
from Sensor import SnowDepthSensor, TemperatureSensor, HumiditySensor, WaterLevelSensor

class SensorDeviceConnector:
	def __init__(self):
		f = open(f'_SensorDeviceConnectorSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.broker = settings['broker']
		self.port = settings['port']
		self.base_topic = settings['base_topic']
		self.id = os.getenv('id', None)
		self.user = os.getenv('user', None)
		self.locality = os.getenv('locality', None)
		self.slope = os.getenv('slope', None)
		self.sector = os.getenv('sector', None)
		self.cannon = os.getenv('cannon', None)
		self.type = os.getenv('type', None)
		self.unit = os.getenv('unit', None)
		f = open('/shared/_ServiceCatalogInfo.json', 'r')
		info = json.load(f)
		f.close()
		self.service_catalog_address = info['service_catalog_address']
		self.service_catalog_port = info['service_catalog_port']
		self.service_catalog_uri = info['service_catalog_uri']
		f = open('/shared/_EnvironmentParameters.json', 'r')
		parameters = json.load(f)
		f.close()
		self.ping_timedelta = parameters['ping_timedelta']
		self.measurements_timedelta = parameters['measurements_timedelta']
		self.MQTTClient = MQTTClient(self.id, self.broker, self.port)
		self.sensors_map = {
			'snow_depth': SnowDepthSensor,
			'temperature': TemperatureSensor,
			'humidity': HumiditySensor,
			'water_level': WaterLevelSensor,
		}
		if self.type in self.sensors_map.keys():
			self.Sensor = self.sensors_map[self.type](self.id, self.broker, self.port, self.type, self.unit)
	
	def start(self):
		self.MQTTClient.start()
	
	def block(self):
		self.ping()
		t_ping = time.time()
		t = time.time()
		while True:
			if time.time() - t_ping >= self.ping_timedelta:
				t_ping = time.time()
				self.ping()
			if time.time() - t >= self.measurements_timedelta:
				t = time.time()
				m = self.Sensor.getMeasurement()
				self.MQTTClient.publish(f'{self.base_topic}/sensor_data/{self.type}/{self.user}/{self.locality}/{self.slope}/{self.sector}/{self.cannon}', json.dumps(m))
			
			
	def stop(self):
		self.MQTTClient.stop()
				
	def ping(self):
		RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={"id": "ResourceCatalog"})
		resourceCatalog = RC.json()
		requests.post(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/sensor', params={'id': self.user, 'loc': self.locality, 'slo': self.slope, 'sec': self.sector}, json = json.dumps(self.Sensor.getSelf()))

if __name__ == '__main__':
	try:
		sensorDeviceConnector = SensorDeviceConnector()
		sensorDeviceConnector.start()
		sensorDeviceConnector.block()
	except:
		sensorDeviceConnector.stop()