#!/usr/bin/python

import serial
import sys
import time
from cloud_lights import CloudLights

def main():
    c = CloudLights(1)
    ser = serial.Serial(sys.argv[1], 19200)

    printCounter = 0

    while True:
        serial_str = c.getCloudLightSerialString()
        ser.write(serial_str)
        ser.flush()
        if printCounter % 4 == 0:
            print serial_str

        printCounter += 1

        time.sleep(0.15)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()
    else:
        print "Usage: [tty name]"
        sys.exit(1)