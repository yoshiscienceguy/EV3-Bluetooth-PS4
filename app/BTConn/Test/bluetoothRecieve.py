import serial
import time

import EV3BT

EV3 = serial.Serial('COM5')
print("Listening for EV3 Bluetooth messages, press CTRL C to quit.")

while 1:
    n = EV3.in_waiting
    if n != 0:
        s = EV3.read(n)

        mail,value,s = EV3BT.decodeMessage(s, EV3BT.MessageType.Logic)
        print(mail,value) 
else:
# No data is ready to be processed
    time.sleep(0.1)

EV3.close()
