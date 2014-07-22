from mosquitto import Mosquitto
from Queue import Queue, Empty
import logging


DAEMON_STATUS = 'home/daemon'
MQTT_HOST = 'localhost'

ON = "1"
OFF = "0"


class MessageCenter(object):
    def __init__(self, client_id):
        client = Mosquitto(client_id, False, self)
        client.will_set(DAEMON_STATUS, OFF, qos=2, retain=True)

        def on_connect(client, self, rc):
            logging.info("MQTT Connected")
            client.publish(DAEMON_STATUS, ON, qos=2, retain=True)
            client.subscribe('home/#')

        def on_disconnect(client, self, rc):
            logging.info("MQTT Disconnected")

        def on_message(client, self, message):
            if self.onMessage is not None:
                self.onMessage(message.topic, message.payload)

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        self.client = client

        self.publish_queue = Queue()
        self.onMessage = None

    def publish(self, topic, payload):
        self.publish_queue.put((topic, payload))

    def runloop(self):
        self.client.connect(MQTT_HOST, keepalive=60)

        while True:
            self.client.loop(timeout=0.1)
            try:
                topic, payload = self.publish_queue.get(block=False)
                self.client.publish(topic, payload, qos=2, retain=True)
                logging.info("MQTT Publish %s: %s" % (topic, payload))
            except Empty, e:
                pass


