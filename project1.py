#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 9/13/2019

""" project1.py: Main python file for EID Project1 to store and display DHT22 data in a QT GUI.

    TODO - project overview

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://github.com/adafruit/Adafruit_Python_DHT

"""

import sys, time, threading
from db import *
from sensor import *
from gui import *

__author__ = "Brian Ibeling"

#-----------------------------------------------------------------------
# Constants
PERIOD_SEC = 10 # TODO - update to 15 sec
MAX_SAMPLE_COUNTS = 5 # TODO - update to 30
#-----------------------------------------------------------------------
# Variables
sampleCount = 0 # Variable to track number of data sample executions

app = QApplication(sys.argv)
mainWindowInstance = MainWindow()
#-----------------------------------------------------------------------

# Method to execute timer every 15 seconds to sample DTH22 sensor
def periodicDth22Sample():
    global sampleCount
    sampleCount = sampleCount + 1;
    
    # Sample DTH22 sensor
    humidity, temperature = sampleDth22()
    
    # If sensor data received, insert to DB and update GUI
    if humidity is not None and temperature is not None:
        insertSensorData(temperature, humidity)
        sensorDataString = 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
        mainWindowInstance.updateCurrentSensorData(sensorDataString)
        print(sensorDataString)
    
    # Trigger timer if timer executed less than MAX_SAMPLE_COUNTS times
    if(sampleCount < MAX_SAMPLE_COUNTS):
        threading.Timer(PERIOD_SEC, periodicDth22Sample).start()
    
    return 0

#-----------------------------------------------------------------------
# Method to launch GUI
def startGui():
    app = QApplication(sys.argv)
    mainWindowInstance.show()
    app.exec_()
    #sys.exit(app.exec_())

#-----------------------------------------------------------------------
def main(args):
    # Initialize connection to mySQL DB and create/open table for sensor data
    initializeDatabase()
    
    periodicDth22Sample()
    
    # Start GUI application
    startGui()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

