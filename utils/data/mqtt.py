import paho.mqtt.client as mqtt_client

from django.conf import settings
from utils.conf import TEMP_ADJ

payload = {'temp': 'Hors ligne'}


def on_connect(client, userdata, rc):
    print("Connection: return code = {}".format(rc))
    print("Connection: Status = {}".format("OK" if rc == 0 else "fail"))


def on_message(client, userdata, message):
    global payload
    if message.topic == "TEMP/TC-01":
        temp_val = int(message.payload.decode("utf8"))
        volts = temp_val / 1023
        temp = "{:.1f}°C".format(((volts - 0.5) * 100) + TEMP_ADJ)
        payload = {'temp': temp}


client = mqtt_client.Client(client_id="client002")

# Assignation des fonctions de rappel
client.on_message = on_message
client.on_connect = on_connect
# client.on_log = on_log

# Connexion broker
client.username_pw_set(username=settings.MQTT_USER, password=settings.MQTT_PSWD)
client.connect(host=settings.MQTT_BROKER, port=settings.MQTT_PORT, keepalive=settings.KEEP_ALIVE)
client.subscribe("TEMP/#")
