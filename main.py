from time import sleep
sleep(5) # this sleep is required for stability
import network
import json
from umqtt.robust import MQTTClient
from mfrc522 import MFRC522
from picozero import RGBLED
from machine import ADC
from math import log

def startWifiConnection(SSID, PASSWORD):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm = 0xa11140) # disable Wi-Fi low power mode
    timeout = 10
    print("Attempting to connect to Wi-Fi")

    while not wlan.isconnected() and timeout > 0:
        wlan.connect(SSID, PASSWORD)
        timeout -= 1
        sleep(1)

    sleep(2)
    print("Connected to Wi-Fi!")

def startBrokerConnection():
    # connect to MQTT broker with reconnect support
    global client
    client = MQTTClient(f"client_{SENSOR_ID}", MQTT_BROKER)
    client.DEBUG = True

    try:
        client.connect()
        print("Connected to MQTT broker!")
    except Exception as e:
        print("Failed to connect to MQTT broker:", e)

def sendMqttPayload(SENSOR_ID, temperature_sensor_reading):
    message_data = {
        "sensorID": SENSOR_ID,
        "temperatureReading": temperature_sensor_reading
    }
    message_json = json.dumps(message_data)

    try:
        client.publish(TOPIC, message_json, retain=True)
        print(f"Published: {message_json}")
    except Exception as e:
        print("Publish failed:",e)

def getRfidReading(reader, allowedIds):
    while True:
        reader.init()
        (status, tag_type) = reader.request(reader.REQIDL)

        if status == reader.OK:
            (status, uid) = reader.SelectTagSN()

        if status == reader.OK:
            cardId = str(int.from_bytes(bytes(uid),"little",False))

        if cardId in allowedIds:
            return True
        else:
            return False

        sleep(.05)

def getTempC(thermistor):
    '''
    This function returns a temperature in Celsius from an analog pin

    :return: Returns the temperature in Celsius
    '''
    V_in = 3.3 #[V]
    R1 = 10000 #[Ohms]

    A = 1.129e-3
    B = 2.341e-4
    C = 8.767e-8

    adcVal = thermistor.read_u16() # 0 to 65535
    vOut = (V_in/65535) * adcVal # [volts]
    Rt = (vOut * R1)/(V_in - vOut) # [ohm], thermistor resistance
    tempK = 1 / (A + (B * log(Rt)) + (C * pow(log(Rt), 3)))
    return (tempK - 273.15)

SSID = "WilfongEngr301"
PASSWORD = "BoilerUp"
MQTT_BROKER = "10.42.0.1"
TOPIC = "pico/data" # pico/data is the label that the subscriber (server) will look for
SENSOR_ID = "Team02"

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)
allowedRfids = ["placeholder"]

redPin = 6
greenPin = 7
bluePin = 8
led = RGBLED(redPin, greenPin, bluePin)
led.color = (255, 0, 0)

thermistor = ADC(27) # Change 27 to whatever analog pin is connected

while True: 
    # must use this variable name for temperature reading
    temperature_sensor_reading = getTempC(thermistor)

    sleep(2)

