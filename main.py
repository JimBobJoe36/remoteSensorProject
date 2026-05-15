############################################################
#################### IMPORT LIBRARIES ######################
############################################################
from time import sleep, ticks_ms           # <<< DO NOT MODIFY >>>
sleep(5) # required for stability          # <<< DO NOT MODIFY >>>

# Imports for MQTT communication           # <<< DO NOT MODIFY >>>
import network                             # <<< DO NOT MODIFY >>>
import json                                # <<< DO NOT MODIFY >>>
from umqtt.robust import MQTTClient        # <<< DO NOT MODIFY >>>
from rotary_irq_esp import RotaryIRQ
from picozero import RGBLED, Button
from machine import ADC, Pin, I2C
from math import log
from mfrc522 import MFRC522
from ssd1306 import SSD1306_I2C

############################################################
################# SPECIFY PINS AND OBJECTS #################
############################################################
rot = RotaryIRQ(
    pin_num_clk=12,
    pin_num_dt=13,
    min_val=0,
    max_val=5,
    reverse=False,
    range_mode=RotaryIRQ.RANGE_WRAP
)

rotDt = Pin(19)
rotClk = Pin(18)
button = Button(20)

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)
allowedRfids = ["450267731"]

thermistor = ADC(28)

led = RGBLED(10, 13, 15)

# OLED object
display_width = 128 # pixel x values = 0 to 127
display_height = 64 # pixel y values = 0 to 63
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000) # TX pin is Pin 0, RX pin is Pin 1
display = SSD1306_I2C(display_width, display_height, i2c)

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
# -------------CODE HERE-------------------

def showText(msg):
    global display

    display.fill(0)
    display.text(msg, 0, 0)
    display.show()

# Thermistor and Temperature
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

# RFID and Badge Reading
def getRfidReading(reader, allowedIds):
    reader.init()
    start = ticks_ms()

    while ticks_ms() - start < 5000:
        (status, tag_type) = reader.request(reader.REQIDL)

        if status == reader.OK:
            (status, uid) = reader.SelectTagSN()
            cardId = str(int.from_bytes(bytes(uid), "little", False))

            return cardId in allowedIds
        else:
            showText("Tap ID.")

        sleep(.1)

    return False

def getRotaryInput(rot, combination):
    showText("Input password.")

    actualCombination = ""
    oldButton = False
    start = ticks_ms()

    while len(actualCombination) < len(combination):
        if ticks_ms() - start > 15000:
            return False

        value = rot.value()

        if button.is_pressed and not oldButton:
            actualCombination += str(value)
            showText(actualCombination)

        oldButton = button.is_pressed
    return actualCombination == combination

# Change LED Based on operational status
def setLED(time, tempVal):
    global led

    if (ticks_ms() - time) > (4*(60*1000)):
        led.color = (0, 0, 255)
    elif (tempVal > 35.0) or (tempVal < 5.0):
        led.color = (255, 0, 0)
    else:
        led.color = (0, 255, 0)

# -----------------------------------------------------
############################################################
####################### INFINITE LOOP ######################
############################################################
unlocked = False
combination = "11111"
lastPublishTime = 0

while True: 
    # !!!-- You must use this variable name: temperature_sensor_reading --!!!
    temperature_sensor_reading = getTempC(thermistor)

    # ------------------------------------------------------------
    # Create and send MQTT payload                               # <<< DO NOT MODIFY >>>
    message_data = {                                             # <<< DO NOT MODIFY >>>
        "sensorID": SENSOR_ID,                                   # <<< DO NOT MODIFY >>>
        "temperatureReading": temperature_sensor_reading         # <<< DO NOT MODIFY >>>
    }                                                            # <<< DO NOT MODIFY >>>
    message_json = json.dumps(message_data)  # Convert to JSON   # <<< DO NOT MODIFY >>>

    # --------------------CODE HERE-------------------------------
    # Note:
    # Device will not transmit data while user is being prompted for ID and password.
    # This basically means that it will not transmit unless device is unlocked.
    # I tried to add a timeout in order to make it transmit infrequently while locked rather than not at all.

    if not unlocked:
        sleep(1)
        idCheck = getRfidReading(reader, allowedRfids)
        passwordCheck = getRotaryInput(rot, combination)

        if idCheck and passwordCheck:
            unlocked = True
            unlockTime = ticks_ms()
            showText("Check passed.")
        else:
            unlocked = False
            showText("Check failed.")

    if unlocked:
        if (ticks_ms() - unlockTime) < (5*(60*1000)):
            if ticks_ms() % 1000 < 100:
                showText(f"Temp: {temperature_sensor_reading}")
            setLED(unlockTime, temperature_sensor_reading)
        else:
            # Locks after 5 minutes
            unlocked = False
            showText("Locking device.")

    if (ticks_ms() - lastPublishTime) >= 2000:
        # Try to publish message to MQTT broker                                    # <<< DO NOT MODIFY >>>
        try:                                                                       # <<< DO NOT MODIFY >>>
            client.publish(TOPIC, message_json, retain=True) # Send MQTT payload   # <<< DO NOT MODIFY >>>
            print(f"Published: {message_json}") # Print MQTT payload to the Shell
        except Exception as e:                                                     # <<< DO NOT MODIFY >>>
            print("Publish failed:",e)

        lastPublishTime = ticks_ms()
    sleep(.1)

