import paho.mqtt.client as PahoMQTT

class MQTTClient:
	def __init__(self, clientID, broker, port, notifier = None):
		self.clientID = clientID
		self.broker = broker
		self.port = port
		self.notifier=notifier

		self._paho_mqtt = PahoMQTT.Client(clientID, True)
		
		self._paho_mqtt.on_connect = self.onConnect
		self._paho_mqtt.on_message = self.onMessageReceived

		self.subscriptions = []

	def start(self):
		print(f"{self.clientID} starting", flush = True)
		self._paho_mqtt.connect(self.broker, self.port)
		self._paho_mqtt.loop_start()

	def stop(self):
		print(f"{self.clientID} stopping", flush = True)
		for topic in self.subscriptions:
			self._paho_mqtt.unsubscribe(topic)
		self.subscriptions = []
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()
    
	def publish(self, topic, message, QoS = 2):
		print(f"{self.clientID} published to {topic}:\n\t{message}", flush = True)
		self._paho_mqtt.publish(topic, message, QoS)
	
	def subscribe(self, topic, QoS = 2):
		print(f"{self.clientID} subscribed to {topic}", flush = True)
		self.subscriptions.append(topic)
		self._paho_mqtt.subscribe(topic, QoS)
	
	def unsubscribe(self, topic):
		if topic in self.subscriptions:
			self._paho_mqtt.unsubscribe(topic)
			self.subscriptions.remove(topic)

	def onConnect(self, paho_mqtt, userdata, flags, rc):
		print(f"{self.clientID} connected to {self.broker} with result code: {rc}", flush = True)

	def onMessageReceived(self, paho_mqtt, userdata, msg):
		print(f"{self.clientID} received from {msg.topic}:\n\t{msg.payload.decode()}", flush = True)
		if self.notifier is not None:
			self.notifier.notify(msg)