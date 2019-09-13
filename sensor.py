#!/usr/bin/env python

""" sensor.py: Interface for DHT22 Temp/Humidity sensor

	Interface to sample temperature and humidity data from the DHT22 sensor.
	This leverages the Adafruit DHT example code, cited below.

	+ Resources and Citations +
	I used the following example code to assist with development of this SW.
		- https://github.com/adafruit/Adafruit_Python_DHT
"""

import sys
import Adafruit_DHT

# Using the DHT22 Temperature and Humidity sensor, connected to GPIO pin 4 on the RPi.
sensor = Adafruit_DHT.DHT22
pin = 4

# TODO - add docstring
def sampleDth22():
	# Read temperature and humidity data from the DHT22 sensor
	humidity, temperature = Adafruit_DHT.read(sensor, pin)

	# Print sensor values (if available)
	if humidity is not None and temperature is not None:
		print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
	else:
		print('Failed to get reading. Try again!')
		sys.exit(1)
