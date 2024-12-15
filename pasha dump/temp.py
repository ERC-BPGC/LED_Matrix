
import serial

import time

s = serial.Serial('/dev/ttyACM1', 115200)

s.write(b'h')
time.sleep(5)
s.write(b'ohs')
print(s.read())

s.close()