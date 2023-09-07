#!/usr/bin/env python

import sys
import json
import cherrypy
import time
sys.path.append('/shared')
from RESTAPI import RESTAPI

class ServiceCatalog:
	def __init__(self):
		f = open('_ServiceCatalogSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.services = settings['services']
		f = open('/shared/_ServiceCatalogInfo.json', 'r')
		info = json.load(f)
		f.close()
		self.address = info['service_catalog_address']
		self.port = info['service_catalog_port']
		self.uri = info['service_catalog_uri']
		f = open('/shared/_EnvironmentParameters.json', 'r')
		parameters = json.load(f)
		f.close()
		self.ping_timedelta = parameters['ping_timedelta']
		self.RESTAPI = RESTAPI(self.uri, self.address, self.port, GET = self.GET, PUT = self.PUT)
		self.busy = False
	
	def start(self):
		self.RESTAPI.start()
	
	def block(self):
		self.RESTAPI.block()
	
	def stop(self):
		self.RESTAPI.stop()
	
	@cherrypy.tools.json_out()
	def GET(self, *uri, **params):
		while self.busy:
			pass
		self.busy = True
		f = open(self.services, "r")
		services = json.load(f)
		f.close()
		t = time.time()
		for service in services["services"]:
			if service["id"] == params["id"]:
				if t - service["timestamp"] >= self.ping_timedelta:
					services["services"].remove(service)
					f = open(self.services, "w")
					json.dump(services, f, separators = (',', ': '), indent = 2)
					f.close()
					self.busy = False
				else:
					self.busy = False
					return service
		self.busy = False
		raise cherrypy.HTTPError(400, "service not found")

	@cherrypy.tools.json_in()   
	def PUT(self, *uri, **params):
		while self.busy:
			pass
		self.busy = True
		f = open(self.services, "r")
		services = json.load(f)
		f.close()
		body = json.loads(cherrypy.request.json)
		body["timestamp"] = time.time()
		for service in services["services"]:
			if service["id"] == body["id"]:
				services["services"].remove(service) #è possibile che siano cambiati ip e port oltre il timestamp
		services["services"].append(body)
		f = open(self.services, "w")
		json.dump(services, f, separators = (',', ': '), indent = 2)
		f.close()
		self.busy = False

if __name__ == "__main__":
	try:
		serviceCatalog = ServiceCatalog()
		serviceCatalog.start()
		serviceCatalog.block()
	except:
		serviceCatalog.stop()