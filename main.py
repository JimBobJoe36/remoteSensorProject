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
allowedRfids = ["placeholder"]

thermistor = ADC(28) # Currently 28, could be set to whatever

led = RGBLED(6,7,8)

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

# Change LED Based on operational status
def setLED(time, tempVal):
    global led
    # TODO Set LED based on "error" codes (temp state)
    # green = functioning normally; red = abnomal value; blue = security re-check required soon
    if tempVal > 30.0:
        led.color = (255,0,0)
    elif (ticks_ms() - time) > 4000:
        led.color = (0,0,255)
    else:
        led.color = (0,255,0)

# Unlock
def unlock():
    if button.is_active:
        print("Button Pressed")
    pass

# -----------------------------------------------------
############################################################
####################### INFINITE LOOP ######################
############################################################
unlocked = False
combination = "13579"
currentTime = ticks_ms()
# TODO Replace all print statements
while True: 
    # !!!-- You must use this variable name: temperature_sensor_reading --!!!
    temperature_sensor_reading = getTempC(thermistor)
    # --------------------CODE HERE-------------------------------
    # Unlock Check
    # TODO Add RFID proof to this for extra security
    if unlocked == True:
        if (ticks_ms() - currentTime) > (5*(60*1000)):
            # OLED should display temperature data here
            display.fill(0)
            display.text(f"Temperature: {temperature_sensor_reading}", 0, 0)
            display.show()
            setLED(currentTime, temperature_sensor_reading)
        else:
            # Locks after 5 minutes
            unlocked = False
            currentTime = ticks_ms()
    else:
        actualCombination = ""
        for i in range(len(combination)):
            value = rot.value()
            if button.is_active == False and oldButton == True:
                actualCombination += str(value)
            oldButton = button.is_active

        if actualCombination == combination:
            print("success")
            currentTime = ticks_ms()
        else:
            actualCombination = ""
            print("failure")


    '''
    else:
        # NOTE May need to put this in the "while" loop.
        #while True:
        val_new = rot.value()
        if val_old != val_new:
            val_old = val_new
            print('result =', val_new)
        if button.is_active == False and oldButton == True:
            print("Button Pressed")
            inp += str(val_old)
            if len(inp) == len(combination):
                if inp == combination:
                    break
                else:
                    print("Wrong combination!")
                    inp = ""
        oldButton = button.is_active
        sleep(0.25)
    '''

    # ------------------------------------------------------------
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

