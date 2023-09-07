#!/usr/bin/env python

import sys
import cherrypy
import requests
import random
import time
import jwt
import json
sys.path.append('/shared')
from RESTAPI import RESTAPI_webpage

class WebServer():

	exposed = True

	def __init__(self):
		f = open('_WebServerSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.uri = settings['uri']
		self.address = settings['address']
		self.port = settings['port']
		self.secret_key = settings['secret_key']
		self.utenti = {"utenti": [{"username": "darior28"}, {"username":"lorenzo"}, {"username":"davide"}, {"username": "giuse"}]}
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
		self.RESTAPI = RESTAPI_webpage(self.uri, self.address, self.port, GET = self.GET, PUT = self.PUT, POST = self.POST, DELETE = self.DELETE)
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
		while(True):
			if time.time() - t_ping >= self.ping_timedelta:
				t_ping = time.time()
				self.ping()
			
	def stop(self):
		self.RESTAPI.stop()
	
	def ping(self):
		requests.put(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', json = json.dumps(self.self))

	def getIP_Port_Uri_From_Service_Catalog(self,name="ResourceCatalog"):
		r = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}?id={name}')
		body = r.json()
		ip = body["address"]
		port = body["port"]
		uri = body["uri"]

		return ip, port, uri
	
	def check_user(self, password):
		ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")

		r = requests.get(f'http://{ip}:{port}/{uri}/auth',params={"tok": str(password)})

		if r.status_code==200:
			return True		
		
		return	False
	
	def generate_token(self, password, expiration):

		ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")

		r = requests.get(f'http://{ip}:{port}/{uri}/auth',params={"tok": str(password)})

		user_data = {"username": "", "tok": str(password), "id": r.text.replace('"', '')}

		payload = {
			"user_data": user_data,
			"exp": time.time() + expiration
		}
		token = jwt.encode(payload, self.secret_key, algorithm="HS256")
		return token

	def GET (self, *uri, **params):

		if len(uri)==0:
			return open("index.html")
		else:
			if uri[0]=="areaPersonale":
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					return open("EditLocality.html")
				except:
					return open("login.html")
				
			elif uri[0]=="logout":
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					cookie = cherrypy.response.cookie #manda i cookie al browser
					cookie['sessionID'] = token
					cookie['sessionID']['path'] = '/'
					cookie['sessionID']['max-age'] = 0
					cookie['sessionID']['version'] = 1
					out= {"canceled": "true"}
					return json.dumps(out)
				except:
					out= {"canceled": "false"}
					return json.dumps(out)
			elif uri[0]=="EditLocality":
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					return open("EditLocality.html")
				except:
					return open("login.html")
			elif uri[0]=="loggedUser":
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					username = decode_token["user_data"]["username"]
					out = {"username": str(username)}
					return json.dumps(out)
				except:
					return open("login.html")
				
					
		if uri[0]=="data_v2":
			if uri[1] == "getMeasure":
				try:
					
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")																		
					thingspeak_info = requests.get(f'http://{ip}:{port}/{uri}/RC/sector/thingspeak_info', params={'loc': params['loc'], 'slo': params['slo'], 'sec': params['sec'], 'tok': str(tok)})
					
					thingspeak_info = thingspeak_info.json()

					ip_thing, port_thing, uri_thing = self.getIP_Port_Uri_From_Service_Catalog(
						name="ThingspeakConnector")
					
					thingspeak_data = requests.get(f'http://{ip_thing}:{port_thing}/{uri_thing}/field', params={
												   'api_key': thingspeak_info['api_key_read'], 'channel_id': thingspeak_info['channel_id'], 'field_id': params['measure'], 'minutes': int(params['ns']) * 60})
					
			
					thingspeak_data = thingspeak_data.json()

					if len(thingspeak_data['feeds']) > 0:
						data = [(e[params['measure']], e['created_at']) for e in thingspeak_data['feeds']]    # field1 sta per SNOW DEPTH
					else:
						data = []
					output = {"data": data}
					return json.dumps(output)
				except:
					return "ERROR Code"
			if uri[1] == "getMeasureCard":
				try:
					
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")																		
					thingspeak_info = requests.get(f'http://{ip}:{port}/{uri}/RC/sector/thingspeak_info', params={'loc': params['loc'], 'slo': params['slo'], 'sec': params['sec'], 'tok': str(tok)})
					
					thingspeak_info = thingspeak_info.json()

					ip_thing, port_thing, uri_thing = self.getIP_Port_Uri_From_Service_Catalog(
						name="ThingspeakConnector")
					
					thingspeak_data = requests.get(f'http://{ip_thing}:{port_thing}/{uri_thing}/field', params={
												   'api_key': thingspeak_info['api_key_read'], 'channel_id': thingspeak_info['channel_id'], 'field_id': params['measure'], 'results': params['ns']})
					
			
					thingspeak_data = thingspeak_data.json()

					if len(thingspeak_data['feeds']) > 0:
						data = [(e[params['measure']], e['created_at']) for e in thingspeak_data['feeds']]    # field1 sta per SNOW DEPTH
					else:
						data = []
					output = {"data": data}
					return json.dumps(output)
				except:
					return "ERROR Code"
		elif uri[0]=="edit":
			
			if uri[1] == "getLocalities":
				try:
					

					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(
						name="Login")

					r = requests.get(
						f'http://{ip}:{port}/{uri}/RC/network/localitiesID', params={'tok': str(tok)})

					output = { "data": json.loads(r.text)}
					return json.dumps(output)

				except:
					return open("login.html")
			elif uri[1]=="getSlopesByLocalityName":
				try:
				
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]
					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")

					r = requests.get(f'http://{ip}:{port}/{uri}/RC/locality/slopesID',params= {'tok': str(tok), 'loc': params['loc']})
					
					output = { "data": json.loads(r.text)}
					return json.dumps(output)
				
				except:
					return open("login.html")
			elif uri[1] == "getSectorsBySlopeNameByLocalityName":
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]
					
					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(
						name="Login")

					r = requests.get(
						f'http://{ip}:{port}/{uri}/RC/slope/sectorsID', params={'tok': str(tok), 'loc': params['loc'], 'slo': params['slo']})

					output = { "data": json.loads(r.text)}
					return json.dumps(output)
				

				except:
					return open("login.html")
	
	def POST(self, *uri, **params):
		if uri[0]=="login":
			body=cherrypy.request.body.read()
			dict_body=json.loads(body)
			if not dict_body:
				raise cherrypy.HTTPError(400, "Bad Request")
			else:
				password = dict_body["password"]

				esito = self.check_user(password) 
				if esito:
					cookie = cherrypy.response.cookie 
					token = self.generate_token(password, 600)
					cookie['sessionID'] = token
					cookie['sessionID']['path'] = '/'
					cookie['sessionID']['max-age'] = 600
					cookie['sessionID']['version'] = 1
					out= {"verified": "true", "username": ""}
					return json.dumps(out)
				else:
					out= {"verified": "false"}
					return json.dumps(out)
		elif uri[0]=="edit":
			body=cherrypy.request.body.read()
			dict_body=json.loads(body)
			if not dict_body:
				raise cherrypy.HTTPError(400, "Bad Request")
			else:
				if uri[1]=="addLocality":
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")

					body_response = {
						"name": dict_body["name"],
						"slopes": []
									}

					r = requests.post(
										f'http://{ip}:{port}/{uri}/RC/locality',params={"tok": str(tok) }, json=json.dumps(body_response))

					return "perfetto"
				if uri[1] == "addSlopeToLocality":
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]


					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")
					slo = {
						'name': dict_body["name"],
						'sectors': []
					}

					r= requests.post(f'http://{ip}:{port}/{uri}/RC/slope', params = {"tok": str(tok), 'loc': dict_body["locality"]}, json = json.dumps(slo))

					return "slope aggiunta"
				if uri[1] == "addSectorToSlopeToLocality":
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					thing_id = decode_token["user_data"]["id"]
					tok = decode_token["user_data"]["tok"]
					locality = dict_body['locality']
					slope = dict_body['slope']
					name = dict_body['name']

					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="ThingspeakConnector")
					channel = requests.post(f'http://{ip}:{port}/{uri}/channel', params = {'name': f'{thing_id}-{locality}-{slope}-{name}', 'description': f'Data referring to sector {name} in slope {slope} at locality {locality}', 'field1': 'snow_depth (mm)', 'field2': 'temperature (°C)', 'field3': 'humidity (%)'}, json = None)
					channel = channel.json()

					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name="Login")
					sec = {
						'name': dict_body["name"],
						'thingspeak_info': {
							'channel_id': channel['id'],
							'api_key_write': channel['api_keys'][0]['api_key'],
							'api_key_read': channel['api_keys'][1]['api_key']
						},
						'cannons': [],
						'sensors':[]
					}

					r= requests.post(f'http://{ip}:{port}/{uri}/RC/sector', params = {"tok": str(tok), 'loc': dict_body["locality"],'slo':dict_body["slope"]}, json = json.dumps(sec))

					return "sector aggiunto"

		return 
	
	def PUT(self, *uri, **params):
		return None
	
	def DELETE (self, *uri,**params):
		if uri[0] == "delete":
			if uri[1] == "locality":
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip_L, port_L, uri_L = self.getIP_Port_Uri_From_Service_Catalog(name = "Login")

					slopesID = requests.get(f'http://{ip_L}:{port_L}/{uri_L}/RC/locality/slopesID', params = {'loc': params['loc'], 'tok': tok})
					slopesID = slopesID.json()
					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name = "ThingspeakConnector")
					success = True
					for slopeID in slopesID:
						sectorsID = requests.get(f'http://{ip_L}:{port_L}/{uri_L}/RC/slope/sectorsID', params = {'loc': params['loc'], 'slo': slopeID, 'tok': tok})
						sectorsID = sectorsID.json()
						for sectorID in sectorsID:
							thingspeak_info = requests.get(f'http://{ip_L}:{port_L}/{uri_L}/RC/sector/thingspeak_info', params = {'loc': params['loc'], 'slo': slopeID, 'sec': sectorID, 'tok': tok})
							thingspeak_info = thingspeak_info.json()
							r = requests.delete(f'http://{ip}:{port}/{uri}/channel', params = {'channel_id': thingspeak_info['channel_id']})
							if r.status_code != 200:
								success = False
					requests.delete(f'http://{ip_L}:{port_L}/{uri_L}/RC/locality', params = {'loc': params['loc'], 'tok': tok})
					if success:
						return json.dumps({'esito': 'locality deleted'})
					else:
						return json.dumps({'esito': 'error'})
						
				except:
					return "ERROR Code"
			elif uri[1] == 'slope':
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip_L, port_L, uri_L = self.getIP_Port_Uri_From_Service_Catalog(name = "Login")
					sectorsID = requests.get(f'http://{ip_L}:{port_L}/{uri_L}/RC/slope/sectorsID', params = {'loc': params['loc'], 'slo': params['slo'], 'tok': tok})
					sectorsID = sectorsID.json()
					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name = "ThingspeakConnector")
					success = True
					for sectorID in sectorsID:
						thingspeak_info = requests.get(f'http://{ip_L}:{port_L}/{uri_L}/RC/sector/thingspeak_info', params = {'loc': params['loc'], 'slo': params['slo'], 'sec': sectorID, 'tok': tok})
						thingspeak_info = thingspeak_info.json()
						r = requests.delete(f'http://{ip}:{port}/{uri}/channel', params = {'channel_id': thingspeak_info['channel_id']})
						if r.status_code != 200:
							success = False
					requests.delete(f'http://{ip_L}:{port_L}/{uri_L}/RC/slope', params = {'loc': params['loc'], 'slo': params['slo'], 'tok': tok})
					if success:
						return json.dumps({'esito': 'slope deleted'})
					else:
						return json.dumps({'esito': 'error'})
						
				except:
					return "ERROR Code"
			elif uri[1] == 'sector':
				try:
					incoming_cookie = cherrypy.request.cookie
					token = incoming_cookie["sessionID"].value
					decode_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
					tok = decode_token["user_data"]["tok"]

					ip_L, port_L, uri_L = self.getIP_Port_Uri_From_Service_Catalog(name = "Login")
					thingspeak_info = requests.get(f'http://{ip_L}:{port_L}/{uri_L}/RC/sector/thingspeak_info', params = {'loc': params['loc'], 'slo': params['slo'], 'sec': params['sec'], 'tok': tok})
					thingspeak_info = thingspeak_info.json()
					ip, port, uri = self.getIP_Port_Uri_From_Service_Catalog(name = "ThingspeakConnector")
					r = requests.delete(f'http://{ip}:{port}/{uri}/channel', params = {'channel_id': thingspeak_info['channel_id']})
					requests.delete(f'http://{ip_L}:{port_L}/{uri_L}/RC/sector', params = {'loc': params['loc'], 'slo': params['slo'], 'sec': params['sec'], 'tok': tok})
					if r.status_code == 200:
						return json.dumps({'esito': 'sector deleted'})
					else:
						return json.dumps({'esito': 'error'})
				except:
					return "ERROR Code"

if __name__ == "__main__":
	try:
		webServer = WebServer()
		webServer.start()
		webServer.block()
	except:
		webServer.stop()