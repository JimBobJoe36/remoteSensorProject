############################################################
#################### IMPORT LIBRARIES ######################
############################################################
from time import sleep                     # <<< DO NOT MODIFY >>>
sleep(5) # required for stability          # <<< DO NOT MODIFY >>>

# Imports for MQTT communication           # <<< DO NOT MODIFY >>>
import network                             # <<< DO NOT MODIFY >>>
import json                                # <<< DO NOT MODIFY >>>
from umqtt.robust import MQTTClient        # <<< DO NOT MODIFY >>>

# Imports the library to make a random number. This is used to
#    create a psuedo temperature value to transmit for demo
#    purposes. You don't need this library for the project.
import random

############################################################
################# SPECIFY PINS AND OBJECTS #################
############################################################



############################################################
##################### OTHER SETUP STUFF ####################
############################################################

# Wi-Fi and MQTT settings
SSID = "WilfongEngr301" # Raspberry Pi 4 Wi-Fi name                               # <<< DO NOT MODIFY >>>
PASSWORD = "BoilerUp" # Raspberry Pi 4 Wi-Fi password, WPA/WPA2 security          # <<< DO NOT MODIFY >>>
MQTT_BROKER = "10.42.0.1"  # Raspberry Pi 4's IP                                  # <<< DO NOT MODIFY >>>
TOPIC = "pico/data" # "pico/data" is just a label                                 # <<< DO NOT MODIFY >>>
                    # It helps organize messages, like folders in a file system.  # <<< DO NOT MODIFY >>>
                    # The TOPIC could be any string, but leave it as "pico/data"  # <<< DO NOT MODIFY >>>

SENSOR_ID = "Team02"  # !!!-- CHANGE THIS AS DIRECTED BY DR. WILFONG --!!!

# Connect to Wi-Fi                                          # <<< DO NOT MODIFY >>>
wlan = network.WLAN(network.STA_IF)                         # <<< DO NOT MODIFY >>>
wlan.active(True)                                           # <<< DO NOT MODIFY >>>
wlan.config(pm = 0xa11140) # disable Wi-Fi low power mode   # <<< DO NOT MODIFY >>>
wlan.connect(SSID, PASSWORD)                                # <<< DO NOT MODIFY >>>

print("Attempting to connect to Wi-Fi")
while not wlan.isconnected():                               # <<< DO NOT MODIFY >>>
    pass                                                    # <<< DO NOT MODIFY >>>

sleep(2)  # Extra delay for stability                       # <<< DO NOT MODIFY >>>
print("Connected to Wi-Fi!")



# Connect to MQTT broker with reconnect support         # <<< DO NOT MODIFY >>>
client = MQTTClient(f"client_{SENSOR_ID}", MQTT_BROKER) # <<< DO NOT MODIFY >>>
client.DEBUG = True                                     # <<< DO NOT MODIFY >>>

# Try to connect to MQTT broker                         # <<< DO NOT MODIFY >>>
try:                                                    # <<< DO NOT MODIFY >>>
    client.connect()                                    # <<< DO NOT MODIFY >>>
    print("Connected to MQTT broker!")
except Exception as e:                                  # <<< DO NOT MODIFY >>>
    print("Failed to connect to MQTT broker:", e)


############################################################
####################### INFINITE LOOP ######################
############################################################
while True: 
    # !!!-- Psuedo temperature sensor reading between 50 and 55 --!!!
    # !!!-- You must use this variable name: temperature_sensor_reading --!!!
    # !!!-- Currently, the temperature reading is just a random number for demo purposes --!!!
    temperature_sensor_reading = random.random()*5 + 50


    
    
    
    # Create and send MQTT payload                               # <<< DO NOT MODIFY >>>
    message_data = {                                             # <<< DO NOT MODIFY >>>
        "sensorID": SENSOR_ID,                                   # <<< DO NOT MODIFY >>>
        "temperatureReading": temperature_sensor_reading         # <<< DO NOT MODIFY >>>
    }                                                            # <<< DO NOT MODIFY >>>
    message_json = json.dumps(message_data)  # Convert to JSON   # <<< DO NOT MODIFY >>>
    
    # Try to publish message to MQTT broker                                    # <<< DO NOT MODIFY >>>
    try:                                                                       # <<< DO NOT MODIFY >>>
        client.publish(TOPIC, message_json, retain=True) # Send MQTT payload   # <<< DO NOT MODIFY >>>
        print(f"Published: {message_json}") # Print MQTT payload to the Shell
    except Exception as e:                                                     # <<< DO NOT MODIFY >>>
        print("Publish failed:",e)
    
    sleep(2) # Send MQTT payload every 2 seconds