import paho.mqtt.client as mqtt
from constance import config

from api.utils import thermal_chamber_use


class MQTTClass(mqtt.Client):
    PAYLOAD = {'temp': 'Hors ligne'}

    def __init__(self, function=None):
        super(MQTTClass, self).__init__(client_id=config.MQTT_CLIENT)
        self.username_pw_set(username=config.MQTT_USER, password=config.MQTT_PSWD)
        self.cntMessage = 0
        self.function = function

    def on_connect(self, client, userdata, flags, rc):
        print("Connection: return code = {} | status = {}".format(rc, "OK" if rc == 0 else "fail"))
        if rc != 0:
            self.PAYLOAD = {'temp': 'Hors ligne'}
            self.stop()

    def on_message(self, client, userdata, message):
        # print(message.topic + " " + str(message.qos) + " " + (message.payload.decode("utf8")))
        try:
            temp_val = int(message.payload.decode("utf8"))
            volts = temp_val / 1023
            temp = "{:.1f}°C".format(((volts - 0.5) * 100) + config.MQTT_TEMP_ADJ)
            self.cntMessage = 0
            thermal_chamber_use(temp)
            print("on_message : {}".format(temp))
            self.PAYLOAD = {'temp': temp}
        except ValueError:
            self.PAYLOAD = {'temp': 'Hors ligne'}

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def result(self):
        self.run()
        self.cntMessage += 1
        print("no result: {} - connected: {}".format(self.cntMessage, self.is_connected()))
        if self.cntMessage >= 2:
            self.PAYLOAD = {'temp': 'Hors ligne'}
            self.stop()
            self.cntMessage = 0
        return self.PAYLOAD

    def run(self):
        try:
            if not self.is_connected():
                self.connect(host=config.MQTT_BROKER, port=config.MQTT_PORT, keepalive=config.KEEP_ALIVE)
                self.subscribe(config.MQTT_TOPIC, 0)
                self.loop_start()
        except OSError:
            print("*** MQTT Server no found ***")
            self.PAYLOAD = {'temp': 'Hors ligne'}
            self.cntMessage = 0

    def stop(self):
        self.loop_stop()
        self.disconnect()
