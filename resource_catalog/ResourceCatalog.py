#!/usr/bin/env python

import sys
import json
import cherrypy
import time
import requests
import uuid
sys.path.append('/shared')
from RESTAPI import RESTAPI

class ResourceCatalog:
	def __init__(self):
		f = open('_ResourceCatalogSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.uri = settings['uri']
		self.address = settings['address']
		self.port = settings['port']
		self.resources_map = settings['resources_map']
		self.resources_folder = settings['resources_folder']
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
		self.RESTAPI = RESTAPI(self.uri, self.address, self.port, GET = self.GET, PUT = self.PUT, POST = self.POST, DELETE = self.DELETE)
		self.self = {
			'id': self.id,
			'uri': self.uri,
			'address': self.address,
			'port': self.port
		}
		self.busy = False
	
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
		for key in ['id']:
			if key not in params.keys():
				self.busy = False
				raise cherrypy.HTTPError(400, f"'{key}' param missing")
		while self.busy:
			pass
		self.busy = True
		f = open(self.resources_map, 'r')
		resources_map = json.load(f)
		f.close()
		if params['id'] not in resources_map.keys():
			resources_map[params['id']] = f'{self.resources_folder}/{uuid.uuid4().hex}.json'
			f = open(self.resources_map, 'w')
			json.dump(resources_map, f, separators = (',', ': '), indent = 2)
			f.close()
			f = open(resources_map[params['id']], "w")
			json.dump({'localities': []}, f, separators = (',', ': '), indent = 2)
			f.close()
		f = open(resources_map[params['id']], "r")
		resources = json.load(f)
		f.close()
		t = time.time()
		for locality in resources['localities']:
			for slope in locality['slopes']:
				for sector in slope['sectors']:
					for cannon in sector['cannons']:
						if t - cannon['timestamp'] >= self.ping_timedelta:
							sector['cannons'].remove(cannon)
					for sensor in sector['sensors']:
						if t - sensor['timestamp'] >= self.ping_timedelta:
							sector['sensors'].remove(sensor)
		f = open(resources_map[params['id']], "w")
		json.dump(resources, f, separators = (',', ': '), indent = 2)
		f.close()
		if len(uri) > 0:
			if uri[0] == 'network':
				if len(uri) == 1:
					self.busy = False
					return resources
				elif len(uri) == 2:
					if uri[1] == 'localitiesID':
						locality_names = []
						for locality in resources['localities']:
							locality_names.append(locality['name'])
						self.busy = False
						return locality_names
					elif uri[1] == 'localities':
						self.busy = False
						return resources['localities']
					elif uri[1] == 'slopesID':
						slope_names = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								slope_names.append(slope['name'])
						self.busy = False
						return slope_names
					elif uri[1] == 'slopes':
						slopes = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								slopes.append(slope)
						self.busy = False
						return slopes
					elif uri[1] == 'sectorsID':
						sector_names = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								for sector in slope['sectors']:
									sector_names.append(sector['name'])
						self.busy = False
						return sector_names
					elif uri[1] == 'sectors':
						sectors = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								for sector in slope['sectors']:
									sectors.append(sector)
						self.busy = False
						return sectors
					elif uri[1] == 'cannonsID':
						cannon_names = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								for sector in slope['sectors']:
									for cannon in sector['cannons']:
										cannon_names.append(cannon['name'])
						self.busy = False
						return cannon_names
					elif uri[1] == 'cannons':
						cannons = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								for sector in slope['sectors']:
									for cannon in sector['cannons']:
										cannons.append(cannon)
						self.busy = False
						return cannons
					elif uri[1] == 'sensorsID':
						sensor_names = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								for sector in slope['sectors']:
									for sensor in sector['sensors']:
										sensor_names.append(sensor['name'])
						self.busy = False
						return sensor_names
					elif uri[1] == 'sensors':
						sensors = []
						for locality in resources['localities']:
							for slope in locality['slopes']:
								for sector in slope['sectors']:
									for sensor in sector['sensors']:
										sensors.append(sensor)
						self.busy = False
						return sensors
				else:
					self.busy = False
					raise cherrypy.HTTPError(400, "URI too long")
			elif uri[0] == 'locality':
				for key in ['loc']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
				if len(uri) == 1:
					for locality in resources['localities']:
						if locality['name'] == params['loc']:
							self.busy = False
							return locality
				elif len(uri) == 2:
					if uri[1] == 'slopesID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								slope_names = []
								for slope in locality['slopes']:
									slope_names.append(slope['name'])
								self.busy = False
								return slope_names
					elif uri[1] == 'slopes':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								self.busy = False
								return locality['slopes']
					elif uri[1] == 'sectorsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								sector_names = []
								for slope in locality['slopes']:
									for sector in slope['sectors']:
										sector_names.append(sector['name'])
								self.busy = False
								return sector_names
					elif uri[1] == 'sectors':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								sectors = []
								for slope in locality['slopes']:
									for sector in slope['sectors']:
										sectors.append(sector)
								self.busy = False
								return sectors
					elif uri[1] == 'cannonsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								cannon_names = []
								for slope in locality['slopes']:
									for sector in slope['sectors']:
										for cannon in sector['cannons']:
											cannon_names.append(cannon['name'])
								self.busy = False
								return cannon_names
					elif uri[1] == 'cannons':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								cannons = []
								for slope in locality['slopes']:
									for sector in slope['sectors']:
										for cannon in sector['cannons']:
											cannons.append(cannon)
								self.busy = False
								return cannons
					elif uri[1] == 'sensorsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								sensor_names = []
								for slope in locality['slopes']:
									for sector in slope['sectors']:
										for sensor in sector['sensors']:
											sensor_names.append(sensor['name'])
								self.busy = False
								return sensor_names
					elif uri[1] == 'sensors':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								sensors = []
								for slope in locality['slopes']:
									for sector in slope['sectors']:
										for sensor in sector['sensors']:
											sensors.append(sensor)
								self.busy = False
								return sensors
				else:
					self.busy = False
					raise cherrypy.HTTPError(400, "URI too long")
			elif uri[0] == 'slope':
				for key in ['loc', 'slo']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
				if len(uri) == 1:
					for locality in resources['localities']:
						if locality['name'] == params['loc']:
							for slope in locality['slopes']:
								if slope['name'] == params['slo']:
									self.busy = False
									return slope
				elif len(uri) == 2:
					if uri[1] == 'sectorsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										sector_names = []
										for sector in slope['sectors']:
											sector_names.append(sector['name'])
										self.busy = False
										return sector_names
					elif uri[1] == 'sectors':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										self.busy = False
										return slope['sectors']
					elif uri[1] == 'cannonsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										cannon_names = []
										for sector in slope['sectors']:
											for cannon in sector['cannons']:
												cannon_names.append(cannon['name'])
										self.busy = False
										return cannon_names
					elif uri[1] == 'cannons':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										cannons = []
										for sector in slope['sectors']:
											for cannon in sector['cannons']:
												cannons.append(cannon)
										self.busy = False
										return cannons
					elif uri[1] == 'sensorsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										sensor_names = []
										for sector in slope['sectors']:
											for sensor in sector['sensors']:
												sensor_names.append(sensor['name'])
										self.busy = False
										return sensor_names
					elif uri[1] == 'sensors':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										sensors = []
										for sector in slope['sectors']:
											for sensor in sector['sensors']:
												sensors.append(sensor)
										self.busy = False
										return sensors
				else:
					self.busy = False
					raise cherrypy.HTTPError(400, "URI too long")
			elif uri[0] == 'sector':
				for key in ['loc', 'slo', 'sec']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
				if len(uri) == 1:
					for locality in resources['localities']:
						if locality['name'] == params['loc']:
							for slope in locality['slopes']:
								if slope['name'] == params['slo']:
									for sector in slope['sectors']:
										if sector['name'] == params['sec']:
											self.busy = False
											return sector
				elif len(uri) == 2:
					if uri[1] == 'cannonsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										for sector in slope['sectors']:
											if sector['name'] == params['sec']:
												cannon_names = []
												for cannon in sector['cannons']:
													cannon_names.append(cannon['name'])
												self.busy = False
												return cannon_names
					elif uri[1] == 'cannons':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										for sector in slope['sectors']:
											if sector['name'] == params['sec']:
												self.busy = False
												return sector['cannons']
					elif uri[1] == 'sensorsID':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										for sector in slope['sectors']:
											if sector['name'] == params['sec']:
												sensor_names = []
												for sensor in sector['sensors']:
													sensor_names.append(sensor['name'])
												self.busy = False
												return sensor_names
					elif uri[1] == 'sensors':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										for sector in slope['sectors']:
											if sector['name'] == params['sec']:
												self.busy = False
												return sector['sensors']
					elif uri[1] == 'thingspeak_info':
						for locality in resources['localities']:
							if locality['name'] == params['loc']:
								for slope in locality['slopes']:
									if slope['name'] == params['slo']:
										for sector in slope['sectors']:
											if sector['name'] == params['sec']:
												self.busy = False
												return sector['thingspeak_info']
				else:
					self.busy = False
					raise cherrypy.HTTPError(400, "URI too long")
			elif uri[0] == 'cannon':
				for key in ['loc', 'slo', 'sec', 'can']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
				if len(uri) == 1:
					for locality in resources['localities']:
						if locality['name'] == params['loc']:
							for slope in locality['slopes']:
								if slope['name'] == params['slo']:
									for sector in slope['sectors']:
										if sector['name'] == params['sec']:
											for cannon in sector['cannons']:
												if cannon['name'] == params['can']:
													self.busy = False
													return cannon
				else:
					self.busy = False
					raise cherrypy.HTTPError(400, "URI too long")
			elif uri[0] == 'sensor':
				for key in ['loc', 'slo', 'sec', 'sen']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
				if len(uri) == 1:
					for locality in resources['localities']:
						if locality['name'] == params['loc']:
							for slope in locality['slopes']:
								if slope['name'] == params['slo']:
									for sector in slope['sectors']:
										if sector['name'] == params['sec']:
											for sensor in sector['sensors']:
												if sensor['name'] == sensors['sen']:
													self.busy = False
													return sensor
				else:
					self.busy = False
					raise cherrypy.HTTPError(400, "URI too long")
		else:
			self.busy = False
			raise cherrypy.HTTPError(400, "URI too short")
		self.busy = False
	
	@cherrypy.tools.json_in()
	def PUT(self, *uri, **params):
		for key in ['id']:
			if key not in params.keys():
				self.busy = False
				raise cherrypy.HTTPError(400, f"'{key}' param missing")
		while self.busy:
			pass
		self.busy = True
		f = open(self.resources_map, 'r')
		resources_map = json.load(f)
		f.close()
		if params['id'] not in resources_map.keys():
			resources_map[params['id']] = f'{self.resources_folder}/{uuid.uuid4().hex}.json'
			f = open(self.resources_map, 'w')
			json.dump(resources_map, f, separators = (',', ': '), indent = 2)
			f.close()
			f = open(resources_map[params['id']], "w")
			json.dump({'localities': []}, f, separators = (',', ': '), indent = 2)
			f.close()
		f = open(resources_map[params['id']], "r")
		resources = json.load(f)  
		f.close()
		body = json.loads(cherrypy.request.json)
		if uri[0] == 'network':
			for locality in resources["localities"]:
				for slope in locality['slopes']:
					for sector in slope['sectors']:
						for cannon in sector['cannons']:
							cannon['info'] = body['info']
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'locality':
			for key in ['loc']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						for sector in slope['sectors']:
							for cannon in sector['cannons']:
								cannon['info'] = body
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'slope':
			for key in ['loc','slo']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								for cannon in sector['cannons']:
									cannon['info'] = body
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'sector':
			for key in ['loc','slo','sec']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									for cannon in sector['cannons']:
										cannon['info'] = body
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'cannon':
			for key in ['loc','slo','sec','can']:
					if key not in params.keys():
						self.busy = False
						raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									for cannon in sector['cannons']:
										if cannon['name'] == params['can']:
											cannon['info'] = body
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		self.busy = False
	
	@cherrypy.tools.json_in()
	def POST(self, *uri, **params):
		for key in ['id']:
			if key not in params.keys():
				self.busy = False
				raise cherrypy.HTTPError(400, f"'{key}' param missing")
		while self.busy:
			pass
		self.busy = True
		f = open(self.resources_map, 'r')
		resources_map = json.load(f)
		f.close()
		if params['id'] not in resources_map.keys():
			resources_map[params['id']] = f'{self.resources_folder}/{uuid.uuid4().hex}.json'
			f = open(self.resources_map, 'w')
			json.dump(resources_map, f, separators = (',', ': '), indent = 2)
			f.close()
			f = open(resources_map[params['id']], "w")
			json.dump({'localities': []}, f, separators = (',', ': '), indent = 2)
			f.close()
		f = open(resources_map[params['id']], "r")
		resources = json.load(f)
		f.close()
		body = json.loads(cherrypy.request.json)
		if uri[0] == 'locality':
			for locality in resources["localities"]:
				if locality['name'] == body['name']:
					self.busy = False
					raise cherrypy.HTTPError(400, f"Locality {body['name']} already present")
			resources["localities"].append(body)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'slope':
			for key in ['loc']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == body['name']:
							self.busy = False
							raise cherrypy.HTTPError(400, f"Slope {body['name']} already present at locality {params['loc']}")
					locality['slopes'].append(body)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'sector':
			for key in ['loc','slo']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == body['name']:
									self.busy = False
									raise cherrypy.HTTPError(400, f"Sector {body['name']} already present in slope {params['slo']} at locality {params['loc']}")
							slope['sectors'].append(body)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'cannon':
			for key in ['loc','slo','sec']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			body['timestamp'] = time.time()
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									for cannon in sector['cannons']:
										if cannon['name'] == body['name']:
											sector['cannons'].remove(cannon)
									sector['cannons'].append(body)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'sensor':
			for key in ['loc','slo','sec']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			body['timestamp'] = time.time()
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									for sensor in sector['sensors']:
										if sensor['name'] == body['name']:
											sector['sensors'].remove(sensor)
									sector['sensors'].append(body)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		self.busy = False

	def DELETE(self, *uri, **params):
		for key in ['id']:
			if key not in params.keys():
				self.busy = False
				raise cherrypy.HTTPError(400, f"'{key}' param missing")
		while self.busy:
			pass
		self.busy = True
		f = open(self.resources_map, 'r')
		resources_map = json.load(f)
		f.close()
		if params['id'] not in resources_map.keys():
			resources_map[params['id']] = f'{self.resources_folder}/{uuid.uuid4().hex}.json'
			f = open(self.resources_map, 'w')
			json.dump(resources_map, f, separators = (',', ': '), indent = 2)
			f.close()
			f = open(resources_map[params['id']], "w")
			json.dump({'localities': []}, f, separators = (',', ': '), indent = 2)
			f.close()
		f = open(resources_map[params['id']], "r")
		resources = json.load(f)
		f.close()
		if uri[0] == 'locality':
			for key in ['loc']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					resources['localities'].remove(locality)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'slope':
			for key in ['loc','slo']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							locality['slopes'].remove(slope)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'sector':
			for key in ['loc','slo','sec']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									slope['sectors'].remove(sector)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'cannon':
			for key in ['loc','slo','sec','can']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			body['timestamp'] = time.time()
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									for cannon in sector['cannons']:
										if cannon['name'] == params['can']:
											sector['cannons'].remove(cannon)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		elif uri[0] == 'sensor':
			for key in ['loc','slo','sec','sen']:
				if key not in params.keys():
					self.busy = False
					raise cherrypy.HTTPError(400, f"'{key}' param missing")
			body['timestamp'] = time.time()
			for locality in resources["localities"]:
				if locality['name'] == params['loc']:
					for slope in locality['slopes']:
						if slope['name'] == params['slo']:
							for sector in slope['sectors']:
								if sector['name'] == params['sec']:
									for sensor in sector['sensors']:
										if sensor['name'] == params['sen']:
											sector['sensors'].remove(sensor)
			f = open(resources_map[params['id']], "w")
			json.dump(resources, f, separators = (',', ': '), indent = 2)
			f.close()
		self.busy = False

if __name__ == "__main__":
	try:
		resourceCatalog = ResourceCatalog()
		resourceCatalog.start()
		resourceCatalog.block()
	except:
		resourceCatalog.stop()