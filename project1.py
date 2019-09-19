#!/usr/bin/env python
#
# ECEN5783
# Author: Brian Ibeling
# 9/13/2019

""" project1.py: Main python file for EID Project1 to store and display DHT22 data in a QT GUI.

	TODO - project overview

	+ Resources and Citations +
	I used the following examples and tutorials to assist with development of this project's SW.
		- https://github.com/adafruit/Adafruit_Python_DHT
		- https://pythonspot.com/mysql-with-python/
		- https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql
		- http://g2pc1.bu.edu/~qzpeng/manual/MySQL%20Commands.htm

"""

import sys
import time, threading
from sensor import sampleDth22
from db import initializeMySql

__author__ = "Brian Ibeling"

#-----------------------------------------------------------------------
# Constants
PERIOD_SEC = 10 # TODO - update to 15 sec
MAX_SAMPLE_COUNTS = 5 # TODO - update to 30
#-----------------------------------------------------------------------
# Variables
sampleCount = 0 # Variable to track number of data sample executions
#-----------------------------------------------------------------------

# Method to execute timer every 15 seconds to sample DTH22 sensor
def periodicDth22Sample():
	global sampleCount
	sampleCount = sampleCount + 1;
	
	# Sample DTH22 sensor
	humidity, temperature = sampleDth22()
	
	# Print received value
	if humidity is not None and temperature is not None:
		print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
	
	# Trigger timer if timer executed less than MAX_SAMPLE_COUNTS times
	if(sampleCount < MAX_SAMPLE_COUNTS):
		threading.Timer(PERIOD_SEC, periodicDth22Sample).start()
	
	return 0

#-----------------------------------------------------------------------
def main(args):
	# Initialize connection to mySQL DB and create/open table for sensor data
	initializeMySql()
	
	periodicDth22Sample()
	
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

