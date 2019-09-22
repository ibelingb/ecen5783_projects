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
PERIOD_SEC = 15
MAX_SAMPLE_COUNTS = 30
#-----------------------------------------------------------------------
# Object Instances and Variables
g_sampleCount = 0 # Variable to track number of data sample executions
g_qtApp = QApplication(sys.argv) # Start QT Application
g_mainWindowInstance = MainWindow() # Create GUI class instance
#-----------------------------------------------------------------------

# Method to execute timer every 15 seconds to sample DTH22 sensor
def periodicDth22Sample():
    global g_sampleCount
    g_sampleCount = g_sampleCount + 1;
    
    # Sample DTH22 sensor
    humidity, temperature = sampleDth22()
    
    # If sensor data received, insert to DB and update GUI
    if humidity is not None and temperature is not None and humidity < 100:
        insertSensorData(temperature, humidity)
        g_mainWindowInstance.updateStatusLine('DB Update: Temp={0:0.1f}*  Humidity={1:0.1f}%' \
                                            .format(temperature, humidity))
    else:
        g_mainWindowInstance.updateStatusLine('Failed to Read Sensor Data')
    
    # Trigger timer if timer executed less than MAX_SAMPLE_COUNTS times.
    # Otherwise, report sensor sampling complete.
    if(g_sampleCount < MAX_SAMPLE_COUNTS):
        threading.Timer(PERIOD_SEC, periodicDth22Sample).start()
    else:
        g_mainWindowInstance.updateStatusLine('Sensor Sampling Complete.')
    
    return 0

#-----------------------------------------------------------------------
# Method to launch GUI
def startGui():
    g_mainWindowInstance.show()
    g_mainWindowInstance.updateStatusLine('Application Started')
    g_mainWindowInstance.updateCurrentSensorData('')
    g_mainWindowInstance.GraphLabel.setText('')
    sys.exit(g_qtApp.exec_())

#-----------------------------------------------------------------------
def main(args):
    # Initialize connection to mySQL DB and create/open table for sensor data
    initializeDatabase()
    
    # Start periodic sampling of sensor data
    periodicDth22Sample()
    
    # Start GUI application
    startGui()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

