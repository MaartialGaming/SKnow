#!/usr/bin/env python

import sys
import json
import time
import requests
import telebot
import threading
sys.path.append('/shared')
from MQTTClient import MQTTClient

class TelegramBot:
	def __init__(self):
		f = open('_TelegramBotSettings.json', 'r')
		settings = json.load(f)
		f.close()
		self.id = settings['id']
		self.broker = settings['broker']
		self.port = settings['port']
		self.base_topic = settings['base_topic']
		self.token = settings['token']
		self.telegram_bot_auth = settings['telegram_bot_auth']
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
		self.bot = telebot.TeleBot(self.token)
		self.define_functions()
		self.MQTTClient = MQTTClient(self.id, self.broker, self.port, notifier = self)
		self.self = {
			'id': self.id,
			'broker': self.broker,
			'port': self.port
		}
		self.filters = {}
			
	def start(self):
		self.MQTTClient.start()
		self.MQTTClient.subscribe(f'{self.base_topic}/telegram_notification/water_level/+/+/+/+/+')
	
	def start_polling(self):
			self.bot.infinity_polling()

	def block(self):
		polling_thread = threading.Thread(target = self.start_polling)
		polling_thread.start()
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

	def define_functions(self):
		def get_structure(id):
			buttons = []
			if len(self.filters[id]) < 4:
				add_filter_button = telebot.types.InlineKeyboardButton('ADD FILTER \U00002795', callback_data = 'add_filter')
			if len(self.filters[id]) > 0:
				remove_filter_button = telebot.types.InlineKeyboardButton('REMOVE FILTER \U00002796', callback_data = 'remove_filter')
			if len(self.filters[id]) < 4:
				network_structure_button = telebot.types.InlineKeyboardButton('NETWORK STRUCTURE \U0001F5C2', callback_data = 'network_structure')
			turn_on_button = telebot.types.InlineKeyboardButton('TURN ON \U00002B06', callback_data = 'turn_on')
			turn_off_button = telebot.types.InlineKeyboardButton('TURN OFF \U00002B07', callback_data = 'turn_off')
			auto_mode_button = telebot.types.InlineKeyboardButton('AUTO MODE \U00002696', callback_data = 'auto_mode')
			set_auto_value_button = telebot.types.InlineKeyboardButton('SET AUTO VALUE \U0001F522', callback_data = 'set_auto_value')
			prog_mode_button = telebot.types.InlineKeyboardButton('PROG MODE \U00002600', callback_data = 'prog_mode')
			set_prog_time_button = telebot.types.InlineKeyboardButton('SET PROG TIME \U0001F552', callback_data = 'set_prog_time')
			toggle_alerts_button = telebot.types.InlineKeyboardButton('TOGGLE ALERTS \U0001F4E3', callback_data = 'toggle_alerts')
			log_out_button = telebot.types.InlineKeyboardButton('LOG OUT \U0001F3C3', callback_data = 'log_out')
			close_menu_button = telebot.types.InlineKeyboardButton('CLOSE MENU \U0000274C', callback_data = 'close_menu')
			
			keyboard = telebot.types.InlineKeyboardMarkup()

			if 0 < len(self.filters[id]) < 4:
				keyboard.add(remove_filter_button, add_filter_button)
			elif len(self.filters[id]) == 0:
				keyboard.add(add_filter_button)
			elif len(self.filters[id]) == 4:
				keyboard.add(remove_filter_button)
			
			if len(self.filters[id]) < 4:
				keyboard.add(network_structure_button)

			keyboard.add(turn_off_button, turn_on_button)

			keyboard.add(auto_mode_button, set_auto_value_button)

			keyboard.add(prog_mode_button, set_prog_time_button)

			keyboard.add(toggle_alerts_button, log_out_button)

			keyboard.add(close_menu_button)

			text = 'Welcome to SKnow!\nCurrent filters:\n'
			if len(self.filters[id]) == 0:
				text += '<None>\n'
			else:
				if len(self.filters[id]) > 0:
					text += f'locality = {self.filters[id][0]}\n'
				if len(self.filters[id]) > 1:
					text += f'slope = {self.filters[id][1]}\n'
				if len(self.filters[id]) > 2:
					text += f'sector = {self.filters[id][2]}\n'
				if len(self.filters[id]) > 3:
					text += f'cannon = {self.filters[id][3]}\n'
			
			return text, keyboard
		
		@self.bot.message_handler(commands=[])
		def process_prog_time(inline_query):
			msg = inline_query.text
			if len(msg) == 11 and msg[5] == '-' and msg[2] == msg[8] == ':' and msg[0:2].isnumeric() and msg[3:5].isnumeric() and msg[6:8].isnumeric() and msg[9:11].isnumeric() and 0 <= int(msg[0:2]) <= 23 and 0 <= int(msg[3:5]) <= 59 and 0 <= int(msg[6:8]) <= 23 and 0 <= int(msg[9:11]) <= 59:
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				user = f'/{auth[str(inline_query.chat.id)]["id"]}'
				topic = f'{self.base_topic}/update_cannons/prog_time'
				topic += user
				for filter in self.filters[inline_query.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, msg)
				self.bot.send_message(inline_query.chat.id, text = f'Programmed time set to {msg}')
				text, keyboard = get_structure(inline_query.chat.id)
				self.bot.send_message(inline_query.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)
			else:
				self.bot.send_message(inline_query.chat.id, text = 'Wrong format!\nInsert working time for the cannon(s). Format:\nhh:mm-hh:mm')
				self.bot.register_next_step_handler(inline_query, process_prog_time)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)
		
		@self.bot.message_handler(commands=[])
		def process_auto_value(inline_query):
			msg = inline_query.text
			if msg.isnumeric():
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				user = f'/{auth[str(inline_query.chat.id)]["id"]}'
				topic = f'{self.base_topic}/update_cannons/auto_value'
				topic += user
				for filter in self.filters[inline_query.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, msg)
				self.bot.send_message(inline_query.chat.id, text = f'Automatic value set to {msg}')
				text, keyboard = get_structure(inline_query.chat.id)
				self.bot.send_message(inline_query.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)
			else:
				self.bot.send_message(inline_query.chat.id, text = 'Wrong format!\nInsert snow depth level (mm) below which cannon(s) start working. Format:\ninteger')
				self.bot.register_next_step_handler(inline_query, process_prog_time)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)
		
		@self.bot.message_handler(commands=[])
		def process_token(inline_query):
			msg = inline_query.text
			L = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params = {"id": "Login"})
			login = L.json()
			res = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/auth', params = {'tok': msg})
			if res.status_code == 200:
				res = res.json()
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				auth[inline_query.chat.id] = {'id': res, 'tok': msg, 'alerts': True}
				f = open(self.telegram_bot_auth, 'w')
				auth = json.dump(auth, f, separators = (',', ': '), indent = 2)
				f.close()
				self.bot.send_message(inline_query.chat.id, text = f'Authenticated')
				text, keyboard = get_structure(inline_query.chat.id)
				self.bot.send_message(inline_query.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)
			elif res.status_code == 401:
				self.bot.send_message(inline_query.chat.id, text = 'Invalid token, please insert a valid authentication token')
				self.bot.register_next_step_handler(inline_query, process_token)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)
			else:
				self.bot.send_message(inline_query.chat.id, text = 'Something went wrong, try inserting the token at a later time')
				self.bot.register_next_step_handler(inline_query, process_token)
				self.bot.delete_message(inline_query.chat.id, inline_query.id - 1)
				self.bot.delete_message(inline_query.chat.id, inline_query.id)

		@self.bot.message_handler(commands=['start'])
		def start(inline_query):
			self.filters[inline_query.chat.id] = []
			f = open(self.telegram_bot_auth, 'r')
			auth = json.load(f)
			f.close()
			if str(inline_query.chat.id) in auth.keys():
				text, keyboard = get_structure(inline_query.chat.id)
				self.bot.send_message(inline_query.chat.id, text = text, reply_markup = keyboard)
			else:
				self.bot.send_message(inline_query.chat.id, text = 'Insert authentication token')
				self.bot.register_next_step_handler(inline_query, process_token)
			self.bot.delete_message(inline_query.chat.id, inline_query.id)
		
		@self.bot.message_handler(commands=['info'])
		def command_info(inline_query):
			text, keyboard = get_info_structure()
			self.bot.send_message(inline_query.chat.id, text = text, reply_markup = keyboard)
			self.bot.delete_message(inline_query.chat.id, inline_query.id)
		
		@self.bot.callback_query_handler(func = lambda call: True)
		def callback_query(call):
			if call.data == 'add_filter':
				L = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params = {'id': 'Login'})
				login = L.json()
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				if len(self.filters[call.message.chat.id]) == 0:
					localitiesID = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/network/localitiesID', params = {'tok': auth[str(call.message.chat.id)]['tok']})
					localitiesID = localitiesID.json()
					buttons = []
					for localityID in localitiesID:
						buttons.append(telebot.types.InlineKeyboardButton(localityID, callback_data = localityID))
					buttons.append(telebot.types.InlineKeyboardButton('BACK \U0001F519', callback_data = 'back'))
					
					keyboard = telebot.types.InlineKeyboardMarkup()
					for button in buttons:
						keyboard.add(button)

					self.bot.send_message(call.message.chat.id, text = 'Choose the locality \U0001F30E', reply_markup = keyboard)
				elif len(self.filters[call.message.chat.id]) == 1:
					slopesID = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/locality/slopesID', params = {'tok': auth[str(call.message.chat.id)]['tok'], 'loc': self.filters[call.message.chat.id][0]})
					slopesID = slopesID.json()
					buttons = []
					for slopeID in slopesID:
						buttons.append(telebot.types.InlineKeyboardButton(slopeID, callback_data = slopeID))
					buttons.append(telebot.types.InlineKeyboardButton('BACK \U0001F519', callback_data = 'back'))
					
					keyboard = telebot.types.InlineKeyboardMarkup()
					for button in buttons:
						keyboard.add(button)

					self.bot.send_message(call.message.chat.id, text = 'Choose the slope \U0001F3D4', reply_markup = keyboard)
				elif len(self.filters[call.message.chat.id]) == 2:
					sectorsID = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/slope/sectorsID', params = {'tok': auth[str(call.message.chat.id)]['tok'], 'loc': self.filters[call.message.chat.id][0], 'slo': self.filters[call.message.chat.id][1]})
					sectorsID = sectorsID.json()
					buttons = []
					for sectorID in sectorsID:
						buttons.append(telebot.types.InlineKeyboardButton(sectorID, callback_data = sectorID))
					buttons.append(telebot.types.InlineKeyboardButton('BACK \U0001F519', callback_data = 'back'))
					
					keyboard = telebot.types.InlineKeyboardMarkup()
					for button in buttons:
						keyboard.add(button)

					self.bot.send_message(call.message.chat.id, text = 'Choose the sector \U0001F4CD', reply_markup = keyboard)
				elif len(self.filters[call.message.chat.id]) == 3:
					cannonsID = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/sector/cannonsID', params = {'tok': auth[str(call.message.chat.id)]['tok'], 'loc': self.filters[call.message.chat.id][0], 'slo': self.filters[call.message.chat.id][1], 'sec': self.filters[call.message.chat.id][2]})
					cannonsID = cannonsID.json()
					buttons = []
					for cannonID in cannonsID:
						buttons.append(telebot.types.InlineKeyboardButton(cannonID, callback_data = cannonID))
					buttons.append(telebot.types.InlineKeyboardButton('BACK \U0001F519', callback_data = 'back'))
					
					keyboard = telebot.types.InlineKeyboardMarkup()
					for button in buttons:
						keyboard.add(button)

					self.bot.send_message(call.message.chat.id, text = 'Choose the cannon \U00002744', reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'remove_filter':
				if len(self.filters[call.message.chat.id]) > 0:
					self.filters[call.message.chat.id].pop(-1)
				text = 'Filters changed to: '
				if len(self.filters[call.message.chat.id]) == 0:
					text += '<None>'
				for filter in self.filters[call.message.chat.id]:
					text += f'{filter}/'
				self.bot.send_message(call.message.chat.id, text = text)
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'turn_on':
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				user = f'/{auth[str(call.message.chat.id)]["id"]}'
				topic = f'{self.base_topic}/update_cannons/mode'
				topic += user
				for filter in self.filters[call.message.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, 'manual')
				topic = f'{self.base_topic}/update_cannons/state'
				topic += user
				for filter in self.filters[call.message.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, 'on')
				self.bot.send_message(call.message.chat.id, 'Cannon(s) turned on')
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'turn_off':
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				user = f'/{auth[str(call.message.chat.id)]["id"]}'
				topic = f'{self.base_topic}/update_cannons/mode'
				topic += user
				for filter in self.filters[call.message.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, 'manual')
				topic = f'{self.base_topic}/update_cannons/state'
				topic += user
				for filter in self.filters[call.message.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, 'off')
				self.bot.send_message(call.message.chat.id, text = 'Cannon(s) turned off')
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'auto_mode':
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				user = f'/{auth[str(call.message.chat.id)]["id"]}'
				topic = f'{self.base_topic}/update_cannons/mode'
				topic += user
				for filter in self.filters[call.message.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, 'auto')
				self.bot.send_message(call.message.chat.id, text = 'Automatic mode activated')
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'set_auto_value':
				self.bot.send_message(call.message.chat.id, text = 'Insert snow depth level (mm) below which cannon(s) start working. Format:\ninteger')
				self.bot.register_next_step_handler(call.message, process_auto_value)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'prog_mode':
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				user = f'/{auth[str(call.message.chat.id)]["id"]}'
				topic = f'{self.base_topic}/update_cannons/mode'
				topic += user
				for filter in self.filters[call.message.chat.id]:
					topic += f'/{filter}'
				self.MQTTClient.publish(topic, 'prog')
				self.bot.send_message(call.message.chat.id, text = 'Programmed mode activated')
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'set_prog_time':
				self.bot.send_message(call.message.chat.id, text = 'Insert working time for the cannon(s). Format:\nhh:mm-hh:mm')
				self.bot.register_next_step_handler(call.message, process_prog_time)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'toggle_alerts':
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				auth[str(call.message.chat.id)]["alerts"] = not auth[str(call.message.chat.id)]["alerts"]
				if auth[str(call.message.chat.id)]["alerts"]:
					self.bot.send_message(call.message.chat.id, text = 'Alerts turned on')
				else:
					self.bot.send_message(call.message.chat.id, text = 'Alerts turned off')
				f = open(self.telegram_bot_auth, 'w')
				auth = json.dump(auth, f, separators = (',', ': '), indent = 2)
				f.close()
			elif call.data == 'log_out':
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				auth.pop(str(call.message.chat.id))
				f = open(self.telegram_bot_auth, 'w')
				auth = json.dump(auth, f, separators = (',', ': '), indent = 2)
				f.close()
				self.bot.send_message(call.message.chat.id, text = 'Insert authentication token')
				self.bot.register_next_step_handler(call.message, process_token)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'back':
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'network_structure':
				L = requests.get(f'http://{self.service_catalog_address}:{self.service_catalog_port}/{self.service_catalog_uri}', params = {'id': 'Login'})
				login = L.json()
				f = open(self.telegram_bot_auth, 'r')
				auth = json.load(f)
				f.close()
				text = 'Structure of '
				if len(self.filters[call.message.chat.id]) == 0:
					text += 'the whole network'
				for filter in self.filters[call.message.chat.id]:
					text += f'{filter}/'
				text += ':\n'
				if len(self.filters[call.message.chat.id]) == 0:
					network = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/network', params = {'tok': auth[str(call.message.chat.id)]['tok']})
					network = network.json()
					for locality in network['localities']:
						text += f'|--{locality["name"]}\n'
						for slope in locality['slopes']:
							text += f'|    |--{slope["name"]}\n'
							for sector in slope['sectors']:
								text += f'|    |    |--{sector["name"]}\n'
								for cannon in sector['cannons']:
									text += f'|    |    |    |--{cannon["name"]}\n'
									text += f'|    |    |    |    |--STATE: {cannon["info"]["state"]}\n'
									text += f'|    |    |    |    |--MODE: {cannon["info"]["mode"]}\n'
									text += f'|    |    |    |    |--AUTO VALUE: {cannon["info"]["auto_value"]}\n'
									text += f'|    |    |    |    |--PROG TIME: {cannon["info"]["prog_time"]}\n'
									if cannon["info"]["water_level"] == None:
										text += f'|    |    |    |    |--WATER LEVEL: -\n'
									else:
										text += f'|    |    |    |    |--WATER LEVEL: {cannon["info"]["water_level"]}\n'
								for sensor in sector['sensors']:
									text += f'|    |    |    |--{sensor["name"]}\n'
									text += f'|    |    |    |    |--TYPE: {sensor["info"]["type"]}\n'
									text += f'|    |    |    |    |--UNIT: {sensor["info"]["unit"]}\n'
				elif len(self.filters[call.message.chat.id]) == 1:
					locality = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/locality', params = {'tok': auth[str(call.message.chat.id)]['tok'], 'loc': self.filters[call.message.chat.id][0]})
					locality = locality.json()
					for slope in locality['slopes']:
						text += f'|--{slope["name"]}\n'
						for sector in slope['sectors']:
							text += f'|    |--{sector["name"]}\n'
							for cannon in sector['cannons']:
								text += f'|    |    |--{cannon["name"]}\n'
								text += f'|    |    |    |--STATE: {cannon["info"]["state"]}\n'
								text += f'|    |    |    |--MODE: {cannon["info"]["mode"]}\n'
								text += f'|    |    |    |--AUTO VALUE: {cannon["info"]["auto_value"]}\n'
								text += f'|    |    |    |--PROG TIME: {cannon["info"]["prog_time"]}\n'
								if cannon["info"]["water_level"] == None:
									text += f'|    |    |    |--WATER LEVEL: -\n'
								else:
									text += f'|    |    |    |--WATER LEVEL: {cannon["info"]["water_level"]}\n'
							for sensor in sector['sensors']:
								text += f'|    |    |--{sensor["name"]}\n'
								text += f'|    |    |    |--TYPE: {sensor["info"]["type"]}\n'
								text += f'|    |    |    |--UNIT: {sensor["info"]["unit"]}\n'
				elif len(self.filters[call.message.chat.id]) == 2:
					slope = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/slope', params = {'tok': auth[str(call.message.chat.id)]['tok'], 'loc': self.filters[call.message.chat.id][0], 'slo': self.filters[call.message.chat.id][1]})
					slope = slope.json()
					for sector in slope['sectors']:
						text += f'|--{sector["name"]}\n'
						for cannon in sector['cannons']:
							text += f'|    |--{cannon["name"]}\n'
							text += f'|    |    |--STATE: {cannon["info"]["state"]}\n'
							text += f'|    |    |--MODE: {cannon["info"]["mode"]}\n'
							text += f'|    |    |--AUTO VALUE: {cannon["info"]["auto_value"]}\n'
							text += f'|    |    |--PROG TIME: {cannon["info"]["prog_time"]}\n'
							if cannon["info"]["water_level"] == None:
								text += f'|    |    |--WATER LEVEL: -\n'
							else:
								text += f'|    |    |--WATER LEVEL: {cannon["info"]["water_level"]}\n'
						for sensor in sector['sensors']:
							text += f'|    |--{sensor["name"]}\n'
							text += f'|    |    |--TYPE: {sensor["info"]["type"]}\n'
							text += f'|    |    |--UNIT: {sensor["info"]["unit"]}\n'
				elif len(self.filters[call.message.chat.id]) == 3:
					sector = requests.get(f'http://{login["address"]}:{login["port"]}/{login["uri"]}/RC/sector', params = {'tok': auth[str(call.message.chat.id)]['tok'], 'loc': self.filters[call.message.chat.id][0], 'slo': self.filters[call.message.chat.id][1], 'sec': self.filters[call.message.chat.id][2]})
					sector = sector.json()
					for cannon in sector['cannons']:
						text += f'|--{cannon["name"]}\n'
						text += f'|    |--STATE: {cannon["info"]["state"]}\n'
						text += f'|    |--MODE: {cannon["info"]["mode"]}\n'
						text += f'|    |--AUTO VALUE: {cannon["info"]["auto_value"]}\n'
						text += f'|    |--PROG TIME: {cannon["info"]["prog_time"]}\n'
						if cannon["info"]["water_level"] == None:
							text += f'|    |--WATER LEVEL: -\n'
						else:
							text += f'|    |--WATER LEVEL: {cannon["info"]["water_level"]}\n'
					for sensor in sector['sensors']:
						text += f'|--{sensor["name"]}\n'
						text += f'|    |--TYPE: {sensor["info"]["type"]}\n'
						text += f'|    |--UNIT: {sensor["info"]["unit"]}\n'
				self.bot.send_message(call.message.chat.id, text = text)
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'close_menu':
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
			else:
				self.filters[call.message.chat.id].append(call.data)
				self.bot.delete_message(call.message.chat.id, call.message.message_id)
				buttons = []
				if len(self.filters[call.message.chat.id]) < 4:
					buttons.append(telebot.types.InlineKeyboardButton('add_filter', callback_data = 'add_filter'))
				if len(self.filters[call.message.chat.id]) > 0:
					buttons.append(telebot.types.InlineKeyboardButton('remove_filter', callback_data = 'remove_filter'))
				text = 'Filters changed to: '
				if len(self.filters[call.message.chat.id]) == 0:
					text += '<None>'
				for filter in self.filters[call.message.chat.id]:
					text += f'{filter}/'
				self.bot.send_message(call.message.chat.id, text = text)
				text, keyboard = get_structure(call.message.chat.id)
				self.bot.send_message(call.message.chat.id, text = text, reply_markup = keyboard)
	
	def notify(self, msg):
		topic = msg.topic.split('/')
		payload = msg.payload.decode()
		f = open(self.telegram_bot_auth, 'r')
		auth = json.load(f)
		f.close()
		for chat_id in auth.keys():
			if auth[chat_id]['id'] == topic[3] and auth[chat_id]['alerts']:
				self.bot.send_message(int(chat_id), text = f'\U000026A0 Water at {payload}%!\n[{topic[4]} - {topic[5]} - {topic[6]} - {topic[7]}]')

if __name__ == '__main__':
	try:
		telegramBot = TelegramBot()
		telegramBot.start()
		telegramBot.block()
	except:
		telegramBot.stop()