#!/usr/bin/env python

import sys
import requests
import json
import time
import cherrypy
sys.path.append('/shared')
from RESTAPI import RESTAPI

class ThingspeakConnector:
	def __init__(self):
		f = open('_ThingspeakConnectorSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.uri = settings['uri']
		self.address = settings['address']
		self.port = settings['port']
		self.user_key = settings['user_key']
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
		self.t_last_publishing = {}
		self.RESTAPI = RESTAPI(self.uri, self.address, self.port, GET = self.GET, POST = self.POST, DELETE = self.DELETE)
		self.self = {
			'id': self.id,
			'uri': self.uri,
			'address': self.address,
			'port': self.port
		}
	
	def start(self):
		self.RESTAPI.start()
	
	def block(self):
		self.ping()
		t_ping = time.time()
		while True:
			if time.time() - t_ping >= self.ping_timedelta:
				t_ping = time.time()
				self.ping()
	
	def stop(self):
		self.RESTAPI.stop()
	
	def ping(self):
		requests.put(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', json = json.dumps(self.self))

	@cherrypy.tools.json_out()
	def GET(self, *uri, **params):
		channel_id = params.pop('channel_id')
		if uri[0] == 'data':
			params['results'] = int(params['results'])
			channel = requests.get(f'https://api.thingspeak.com/channels/{channel_id}/feeds.json', params = params, json = None)
			return channel.json()
		elif uri[0] == 'field':
			if 'results' in params.keys():
				params['results'] = int(params['results'])
				results = params.pop('results')
				field_id = params.pop('field_id')

				channel = requests.get(f'https://api.thingspeak.com/channels/{channel_id}/fields/{field_id[-1]}.json', params = params, json = None)
				channel = channel.json()
				filtered_feeds = []
				feeds_number = 0
				for feed in channel['feeds'][::-1]:
					if feed[field_id] != None and feeds_number < results:
						filtered_feeds.append(feed)
						feeds_number += 1
				channel['feeds'] = filtered_feeds[::-1]
				return channel
			elif 'minutes' in params.keys():
				params['minutes'] = int(params['minutes'])
				field_id = params.pop('field_id')
				channel = requests.get(f'https://api.thingspeak.com/channels/{channel_id}/fields/{field_id[-1]}.json', params = params, json = None)
				channel = channel.json()
				filtered_feeds = []
				for feed in channel['feeds'][::-1]:
					if feed[field_id] != None:
						filtered_feeds.append(feed)
				channel['feeds'] = filtered_feeds[::-1]
				return channel

	@cherrypy.tools.json_out()
	def POST(self, *uri, **params):
		if uri[0] == 'channel':
			params['api_key'] = self.user_key
			channel = requests.post(f'https://api.thingspeak.com/channels.json', params = params, json = None)
			return channel.json()
		elif uri[0] == 'data':
			if params['api_key'] in self.t_last_publishing.keys():
				while time.time() - self.t_last_publishing[params['api_key']] <= 20:
					pass
			self.t_last_publishing[params['api_key']] = time.time()
			if 'field1' in params.keys():
				params['field1'] = int(params['field1'])
			if 'field2' in params.keys():
				params['field2'] = float(params['field2'])
			if 'field3' in params.keys():
				params['field3'] = int(params['field3'])
			res = requests.post(f'https://api.thingspeak.com/update.json', params = params, json = None)
	
	def DELETE(self, *uri, **params):
		params['api_key'] = self.user_key
		channel_id = params.pop('channel_id')
		if uri[0] == 'channel':
			channel = requests.delete(f'https://api.thingspeak.com/channels/{channel_id}.json', params = params, json = None)

if __name__ == '__main__':
	try:
		thingspeakConnector = ThingspeakConnector()
		thingspeakConnector.start()
		thingspeakConnector.block()
	except:
		thingspeakConnector.stop()