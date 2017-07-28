#!/usr/bin/python

import threading
import time
import signal
import sys
import urllib2
import traceback
import serial
import RPi.GPIO as GPIO

from cloud_lights import CloudLights

NUM_CLOUD_LIGHTS = 15
CLOUD_UPDATE_TIME = 0.1

last_button_press_time = 0

def _makeSerialOrNone(shouldLogError):
    try:
        return serial.Serial("/dev/ttyACM0", 19200)
    except serial.serialutil.SerialException:
        if shouldLogError:
            traceback.print_exc()
        return None

def main():
    # set up pins
    lastInputCheckTime = 0

    # cloud effects
    c = CloudLights(NUM_CLOUD_LIGHTS)
    ser = _makeSerialOrNone(True)

    lastCloudUpdateTime = 0

    while True:
        currTime = time.time()
        if currTime - lastCloudUpdateTime >= CLOUD_UPDATE_TIME:
            lastCloudUpdateTime = currTime
            if ser:
                serString = c.getCloudLightSerialString()
                try:
                    ser.write(serString)
                except serial.serialutil.SerialException:
                    traceback.print_exc()
                    ser = None
            else:
                ser = _makeSerialOrNone(False)

if __name__ == "__main__":
    main()
