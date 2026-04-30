from machine import ADC
from math import log

thermistor = ADC(27) # Change 27 to whatever analog pin is connected

def getTempC():
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