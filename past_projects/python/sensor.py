#!/usr/bin/python3

""" sensor.py: Interface for DHT22 Temp/Humidity sensor

    Interface to sample temperature and humidity data from the DHT22 sensor.
    This leverages the Adafruit DHT example code, cited below.

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://github.com/adafruit/Adafruit_Python_DHT
        - https://zeromq.org/languages/python/
"""

import sys
import Adafruit_DHT
from datetime import datetime
import json
import zmq

__author__ = "Brian Ibeling"
#-----------------------------------------------------------------------
# Using the DHT22 Temperature and Humidity sensor, connected to GPIO pin 4 on the RPi.
SENSOR = Adafruit_DHT.DHT22
PIN = 4

context = zmq.Context()
dataSocket = context.socket(zmq.REQ)
dataSocket.connect("tcp://localhost:5555")
#-----------------------------------------------------------------------
def sampleDth22():
    """ Read humidity and temperature data from the DHT22 sensor, returning data in that order """
    humidity, temperature = Adafruit_DHT.read(SENSOR, PIN)

    # If sensor samples properly read, push to AWS IoT
    if humidity is not None and temperature is not None and humidity < 100:
      # Populate JSON object with sensor data
      sensorData = '{  "recordType": "data"' \
                   ',  "timestamp": "'   + str(datetime.now()) + \
                   '", "temperature": "' + str(round(temperature,1)) + \
                   '", "humidity": "'    + str(round(humidity, 1)) + '"}'
      # Pass data to data_pusher.py via ZeroMQ socket
      dataSocket.send_string(sensorData)
      dataSocket.recv_string()

    return humidity, temperature

#-----------------------------------------------------------------------
