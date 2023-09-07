#!/usr/bin/env python

import sys
import os
import requests
import json
import time
import random
sys.path.append('/shared')
from MQTTClient import MQTTClient
from SnowCannon import SnowCannon

class SnowCannonDeviceConnector:
	def __init__(self):
		f = open(f'_SnowCannonDeviceConnectorSettings.json', 'r')
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
		self.MQTTClient = MQTTClient(self.id, self.broker, self.port, notifier = self)
		self.SnowCannon = SnowCannon(self.id, self.broker, self.port)
	
	def start(self):
		self.MQTTClient.start()
		self.MQTTClient.subscribe(f'{self.base_topic}/update_cannons/+/{self.user}')
		self.MQTTClient.subscribe(f'{self.base_topic}/update_cannons/+/{self.user}/{self.locality}')
		self.MQTTClient.subscribe(f'{self.base_topic}/update_cannons/+/{self.user}/{self.locality}/{self.slope}')
		self.MQTTClient.subscribe(f'{self.base_topic}/update_cannons/+/{self.user}/{self.locality}/{self.slope}/{self.sector}')
		self.MQTTClient.subscribe(f'{self.base_topic}/update_cannons/+/{self.user}/{self.locality}/{self.slope}/{self.sector}/{self.id}')
	
	def block(self):
		self.ping()
		t_ping = time.time()
		t = time.time()
		while True:
			if time.time() - t_ping >= self.ping_timedelta:
				t_ping = time.time()
				self.ping()
			if time.time() - t >= 1:
				t = time.time()
				if self.SnowCannon.getState() == 'on':
					to_print = ""
					for i in range(50):
						if random.random() <= 0.5:
							to_print += " "
						else:
							to_print += "'"
					print(to_print, flush = True)
	
	def stop(self):
		self.MQTTClient.stop()
	
	def notify(self, msg):
		topic = msg.topic.split('/')
		payload = msg.payload.decode()
		SC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={"id": "ResourceCatalog"})
		resourceCatalog = SC.json()
		if topic[2] == 'state':
			self.SnowCannon.setState(payload)
		elif topic[2] == 'mode':
			self.SnowCannon.setMode(payload)
		elif topic[2] == 'auto_value':
			self.SnowCannon.setAutoValue(payload)
		elif topic[2] == 'prog_time':
			self.SnowCannon.setProgTime(payload)
		elif topic[2] == 'water_level':
			self.SnowCannon.setWaterLevel(payload)
		requests.put(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/cannon', params={'id': self.user, 'loc': self.locality, 'slo': self.slope, 'sec': self.sector, 'can': self.id}, json = json.dumps(self.SnowCannon.getInfo()))

				
	def ping(self):
		RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={"id": "ResourceCatalog"})
		resourceCatalog = RC.json()
		requests.post(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/cannon', params={'id': self.user, 'loc': self.locality, 'slo': self.slope, 'sec': self.sector}, json = json.dumps(self.SnowCannon.getSelf()))

if __name__ == '__main__':
	try:
		snowCannonDeviceConnector = SnowCannonDeviceConnector()
		snowCannonDeviceConnector.start()
		snowCannonDeviceConnector.block()
	except:
		snowCannonDeviceConnector.stop()