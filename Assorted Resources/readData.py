from mfrc522 import MFRC522
from time import sleep
from machine import RTC

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)
rtc = RTC()

detecting = False

while True:
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)

    # Get date time info
    (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()

    # If we were not previously detecting and we are now detecting then print data and mark previous detection
    if (detecting == False and stat == reader.OK):
        detecting = True
        (stat, uid) = reader.SelectTagSN()
        card = int.from_bytes(bytes(uid),"little",False)
        #print("{:04}-{:02}-{:02} @ {:02}:{:02}:{:02} | ID: ".format(year, month, day, hours, minutes, seconds) + str(card) + "\n")

        '''with open("log.txt", "a") as file:
            file.write("{:04}-{:02}-{:02} @ {:02}:{:02}:{:02} | ID: ".format(year, month, day, hours, minutes, seconds) + str(card) + "\n")'''

    # If we were detecting and no longer detecting then mark as no longer detecting
    elif (detecting == True and stat == reader.ERR):
        detecting = False

    sleep(.05)

