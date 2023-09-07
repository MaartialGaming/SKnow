#!/usr/bin/env python

import sys
import time
import requests
import json
sys.path.append('/shared')
from MQTTClient import MQTTClient

class WaterLevelControl:
	def __init__(self):
		f = open('_WaterLevelControlSettings.json', 'r')
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
		self.automations_timedelta = parameters['automations_timedelta']
		self.MQTTClient = MQTTClient(self.id, self.broker, self.port, notifier = self)
		self.self = {
			'id': self.id,
			'broker': self.broker,
			'port': self.port
		}
	
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
			if time.time() - t >= self.automations_timedelta:
				t = time.time()
				RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={"id": "ResourceCatalog"})
				resourceCatalog = RC.json()
				L = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={"id": "Login"})
				login = L.json()
				users = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/users', params={})
				users = users.json()
				for user in users:
					localitiesID = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/network/localitiesID', params={'id': user})
					localitiesID = localitiesID.json()
					for localityID in localitiesID:
						slopesID = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/locality/slopesID', params={'id': user, 'loc': localityID})
						slopesID = slopesID.json()
						for slopeID in slopesID:
							sectorsID = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/slope/sectorsID', params={'id': user, 'loc': localityID, 'slo': slopeID})
							sectorsID = sectorsID.json()
							for sectorID in sectorsID:
								cannons = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/sector/cannons', params={'id': user, 'loc': localityID, 'slo': slopeID, 'sec': sectorID})
								cannons = cannons.json()
								for cannon in cannons:
									if cannon['info']['water_level'] is not None and cannon['info']['water_level'] <= 20:
										self.MQTTClient.publish(f'{self.base_topic}/telegram_notification/water_level/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', cannon['info']['water_level'])

	def stop(self):
		self.MQTTClient.stop()
	
	def ping(self):
		requests.put(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', json = json.dumps(self.self))

if __name__ == '__main__':
	try:
		waterLevelControl = WaterLevelControl()
		waterLevelControl.start()
		waterLevelControl.block()
	except:
		waterLevelControl.stop()