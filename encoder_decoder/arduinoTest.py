import serial
import time

# Initialize the serial connection (adjust the port and baud rate as needed)
arduino = serial.Serial(port='COM11', baudrate=9600, timeout=.01)

while True:
    num = input("Enter a number: ")
    arduino.write(bytearray([65,66]))
    print(arduino.read(5))
