import serial
import time
import EV3BT

EV3 = serial.Serial('COM10')

for i in range(1000):
    s = EV3BT.encodeMessage(EV3BT.MessageType.Text, 'abc', str(i))
    print(EV3BT.printMessage(s))
    EV3.write(s)
    time.sleep(.01)
EV3.close()
