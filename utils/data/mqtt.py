import paho.mqtt.client as mqtt_client

from utils import conf as config

payload = {'temp': 'Hors ligne'}


def on_connect(client, userdata, rc):
    print("Connection: return code = {}".format(rc))
    print("Connection: Status = {}".format("OK" if rc == 0 else "fail"))


def on_message(client, userdata, message):
    global payload
    if message.topic == "TEMP/TC-01":
        temp_val = int(message.payload.decode("utf8"))
        volts = temp_val / 1023
        temp = "{:.1f}°C".format(((volts - 0.5) * 100) + config.TEMP_ADJ)
        payload = {'temp': temp}


client = mqtt_client.Client(client_id=config.MQTT_CLIENT)

# Assignation des fonctions de rappel
client.on_message = on_message
client.on_connect = on_connect

# Connexion broker
client.username_pw_set(username=config.MQTT_USER, password=config.MQTT_PSWD)
client.connect(host=config.MQTT_BROKER, port=config.MQTT_PORT, keepalive=config.KEEP_ALIVE)
client.subscribe("TEMP/#")
