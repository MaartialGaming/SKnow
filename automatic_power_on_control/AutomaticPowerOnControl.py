#!/usr/bin/env python

import sys
import time
import requests
import datetime
import json
sys.path.append('/shared')
from MQTTClient import MQTTClient

class AutomaticPowerOnControl:
	def __init__(self):
		f = open('_AutomaticPowerOnControlSettings.json', 'r')
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
								thingspeak_info = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/sector/thingspeak_info', params={'id': user, 'loc': localityID, 'slo': slopeID, 'sec': sectorID})
								thingspeak_info = thingspeak_info.json()
								TC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params = {"id": "ThingspeakConnector"})
								thingspeakConnector = TC.json()
								thingspeak_data = requests.get(f'http://{thingspeakConnector["address"]}:{thingspeakConnector["port"]}/{thingspeakConnector["uri"]}/field', params = {'api_key': thingspeak_info['api_key_read'], 'channel_id': thingspeak_info['channel_id'], 'field_id': 'field1', 'results': 1})
								thingspeak_data = thingspeak_data.json()
								if len(thingspeak_data['feeds']) > 0:
									average_sector_snow_depth = float(thingspeak_data['feeds'][0]['field1'])
								cannons = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/sector/cannons', params={'id': user, 'loc': localityID, 'slo': slopeID, 'sec': sectorID})
								cannons = cannons.json()
								for cannon in cannons:
									if cannon['info']['mode'] == 'auto' and len(thingspeak_data['feeds']) > 0:
										if average_sector_snow_depth < cannon['info']['auto_value']:
											self.MQTTClient.publish(f'{self.base_topic}/update_cannons/state/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', 'on')
										else:
											self.MQTTClient.publish(f'{self.base_topic}/update_cannons/state/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', 'off')
									elif cannon['info']['mode'] == 'prog':
										now_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%H:%M'), '%H:%M')
										prog_time = cannon['info']['prog_time']
										prog_on = datetime.datetime.strptime(prog_time[0:5], '%H:%M')
										prog_off = datetime.datetime.strptime(prog_time[6:11], '%H:%M')
										if prog_off >= prog_on:
											if prog_off >= now_time >= prog_on:
												self.MQTTClient.publish(f'{self.base_topic}/update_cannons/state/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', 'on')
											else:
												self.MQTTClient.publish(f'{self.base_topic}/update_cannons/state/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', 'off')
										else:
											if prog_on > now_time > prog_off:
												self.MQTTClient.publish(f'{self.base_topic}/update_cannons/state/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', 'off')
											else:
												self.MQTTClient.publish(f'{self.base_topic}/update_cannons/state/{user}/{localityID}/{slopeID}/{sectorID}/{cannon["name"]}', 'on')

	def stop(self):
		self.MQTTClient.stop()
	
	def ping(self):
		requests.put(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', json = json.dumps(self.self))

if __name__ == '__main__':
	try:
		automaticPowerOnControl = AutomaticPowerOnControl()
		automaticPowerOnControl.start()
		automaticPowerOnControl.block()
	except:
		automaticPowerOnControl.stop()