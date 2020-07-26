import serial
import time

# ser = serial.Serial('COM3', 9600)
ser = serial.Serial('COM3',9600)
time.sleep(2)


while True:
    data = ser.readline()
    # print(type(data))
    str_data = data.decode().rstrip()
    print(str_data)
    # time.sleep(1)