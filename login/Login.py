#!/usr/bin/env python

import sys
import time
import requests
import json
import cherrypy
import uuid
sys.path.append('/shared')
from RESTAPI import RESTAPI

class Login:
	def __init__(self):
		f = open('_LoginSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.uri = settings['uri']
		self.address = settings['address']
		self.port = settings['port']
		self.users = settings['users']
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
		self.RESTAPI = RESTAPI(self.uri, self.address, self.port, GET = self.GET, POST = self.POST, PUT = self.PUT, DELETE = self.DELETE)
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
		if uri[0] == 'auth':
			for key in ['tok']:
				if key not in params.keys():
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			for user in users.keys():
				if user == params['tok']:
					return users[user]
			raise cherrypy.HTTPError(401, 'Unhautorized')
		elif uri[0] == 'users':
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			return list(users.values())
		elif uri[0] == 'RC':
			for key in ['tok']:
				if key not in params.keys():
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			for tok in users.keys():
				if tok == params['tok']:
					RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={'id': 'ResourceCatalog'})
					resourceCatalog = RC.json()
					new_uri = ''
					for element in uri[1:]:
						new_uri += f'{element}/'
					params.pop('tok')
					params['id'] = users[tok]
					res = requests.get(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/{new_uri}', params = params)
					return res.json()
			raise cherrypy.HTTPError(401, 'Unhautorized')
			
	@cherrypy.tools.json_in()
	def POST(self, *uri, **params):
		if uri[0] == 'user':
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			body = json.loads(cherrypy.request.json)
			tok = uuid.uuid4().hex
			id = f'{body["id"]}_{uuid.uuid4().hex}'
			users[tok] = id
			f = open(self.users, 'w')
			json.dump(users, f, separators = (',', ': '), indent = 2)
			f.close()
			return json.dumps({'id': id, 'tok': tok})
		elif uri[0] == 'RC':
			for key in ['tok']:
				if key not in params.keys():
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			for tok in users.keys():
				if tok == params['tok']:
					RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={'id': 'ResourceCatalog'})
					resourceCatalog = RC.json()
					new_uri = ''
					for element in uri[1:]:
						new_uri += f'{element}/'
					params.pop('tok')
					params['id'] = users[tok]
					res = requests.post(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/{new_uri}', params = params, json = cherrypy.request.json)
					return res
			raise cherrypy.HTTPError(401, 'Unhautorized')
	
	@cherrypy.tools.json_in()
	def PUT(self, *uri, **params):
		if uri[0] == 'RC':
			for key in ['tok']:
				if key not in params.keys():
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			for tok in users.keys():
				if tok == params['tok']:
					RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={'id': 'ResourceCatalog'})
					resourceCatalog = RC.json()
					new_uri = ''
					for element in uri[1:]:
						new_uri += f'{element}/'
					params.pop('tok')
					params['id'] = users[tok]
					res = requests.put(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/{new_uri}', params = params, json = cherrypy.request.json)
					return res
			raise cherrypy.HTTPError(401, 'Unhautorized')
	
	def DELETE(self, *uri, **params):
		if uri[0] == 'RC':
			for key in ['tok']:
				if key not in params.keys():
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			f = open(self.users, 'r')
			users = json.load(f)
			f.close()
			for tok in users.keys():
				if tok == params['tok']:
					RC = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params={'id': 'ResourceCatalog'})
					resourceCatalog = RC.json()
					new_uri = ''
					for element in uri[1:]:
						new_uri += f'{element}/'
					params.pop('tok')
					params['id'] = users[tok]
					res = requests.delete(f'http://{resourceCatalog["address"]}:{resourceCatalog["port"]}/{resourceCatalog["uri"]}/{new_uri}', params = params)
					return res
			raise cherrypy.HTTPError(401, 'Unhautorized')

if __name__ == '__main__':
	try:
		login = Login()
		login.start()
		login.block()
	except:
		login.stop()