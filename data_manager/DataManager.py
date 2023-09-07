#!/usr/bin/env python

import sys
import requests
import time
import json
sys.path.append('/shared')
from MQTTClient import MQTTClient

class DataManager:
	def __init__(self):
		f = open('_DataManagerSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.broker = settings['broker']
		self.port = settings['port']
		self.base_topic = settings['base_topic']
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
		self.type_to_field_map = {
			'snow_depth': 'field1',
			'temperature': 'field2',
			'humidity': 'field3',
		}
		self.self = {
			'id': self.id,
			'broker': self.broker,
			'port': self.port
		}
	
	def start(self):
		self.MQTTClient.start()
		self.MQTTClient.subscribe(f'{self.base_topic}/sensor_data/+/+/+/+/+/+')
	
	def block(self):
		self.ping()
		t_ping = time.time()
		while True:
			if time.time() - t_ping >= self.ping_timedelta:
				t_ping = time.time()
				self.ping()

	def stop(self):
		self.MQTTClient.stop()
	
	def ping(self):
		requests.put(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', json = json.dumps(self.self))
	
	def notify(self, msg):
		topic = msg.topic.split('/')
		payload = json.loads(msg.payload.decode())
		RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={"id": "ResourceCatalog"})
		resourceCatalog = RC.json()
		if topic[2] in self.type_to_field_map:
			thingspeak_info = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/sector/thingspeak_info', params = {'id': topic[3], 'loc': topic[4], 'slo': topic[5], 'sec': topic[6]})
			thingspeak_info = thingspeak_info.json()
			if thingspeak_info != None:
				TC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params = {"id": "ThingspeakConnector"})
				thingspeakConnector = TC.json()
				requests.post(f'http://{thingspeakConnector["address"]}:{thingspeakConnector["port"]}/{thingspeakConnector["uri"]}/data', params = {'api_key': thingspeak_info['api_key_write'], self.type_to_field_map[topic[2]]: payload['value']})
		elif topic[2] == 'water_level':
			self.MQTTClient.publish(f'{self.base_topic}/update_cannons/{topic[2]}/{topic[3]}/{topic[4]}/{topic[5]}/{topic[6]}/{topic[7]}', payload['value'])

if __name__ == '__main__':
	try:
		dataManager = DataManager()
		dataManager.start()
		dataManager.block()
	except:
		dataManager.stop()