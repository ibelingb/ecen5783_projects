#!/usr/bin/python3

""" sensor.py: Interface for DHT22 Temp/Humidity sensor

    Interface to sample temperature and humidity data from the DHT22 sensor.
    This leverages the Adafruit DHT example code, cited below.

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://github.com/adafruit/Adafruit_Python_DHT
"""

import sys
import Adafruit_DHT

__author__ = "Brian Ibeling"

# Using the DHT22 Temperature and Humidity sensor, connected to GPIO pin 4 on the RPi.
SENSOR = Adafruit_DHT.DHT22
PIN = 4

#-----------------------------------------------------------------------
def sampleDth22():
    # Read temperature and humidity data from the DHT22 sensor
    humidity, temperature = Adafruit_DHT.read(SENSOR, PIN)
    return humidity, temperature

#-----------------------------------------------------------------------
