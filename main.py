from time import sleep
sleep(5) # this sleep is required for stability
import network
import json
from umqtt.robust import MQTTClient

SSID = "WilfongEngr301"
PASSWORD = "BoilerUp"
MQTT_BROKER = "10.42.0.1"
TOPIC = "pico/data" # pico/data is the label that the subscriber (server) will look for
SENSOR_ID = "Team02"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140) # disable Wi-Fi low power mode
wlan.connect(SSID, PASSWORD)

print("Attempting to connect to Wi-Fi")
while not wlan.isconnected():
    pass

sleep(2)  # extra delay for stability
print("Connected to Wi-Fi!")

# connect to MQTT broker with reconnect support
client = MQTTClient(f"client_{SENSOR_ID}", MQTT_BROKER)
client.DEBUG = True

try:
    client.connect()
    print("Connected to MQTT broker!")
except Exception as e:
    print("Failed to connect to MQTT broker:", e)


while True: 
    # must use this variable name for temperature reading
    temperature_sensor_reading = 0

    # create and send MQTT payload
    message_data = {
        "sensorID": SENSOR_ID,
        "temperatureReading": temperature_sensor_reading
    }
    message_json = json.dumps(message_data)

    try:
        # send the payload
        client.publish(TOPIC, message_json, retain=True)
        print(f"Published: {message_json}")
    except Exception as e:
        print("Publish failed:",e)

    sleep(2)

