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
        - https://docs.python.org/2/library/threading.html

"""

import sys, time, threading
from db import *
from sensor import *
from gui import *

__author__ = "Brian Ibeling"

#-----------------------------------------------------------------------
# Constants
PERIOD_SEC = 15
TIMER_START_DELAY_SEC = 3 # Delay for sensor sample timer to allow GUI to start before first sample
MAX_SAMPLE_COUNTS = 30
#-----------------------------------------------------------------------
# Object Instances and Variables
g_sampleCount = 0 # Variable to track number of data sample executions
g_qtApp = QApplication(sys.argv) # Start QT Application
g_mainWindowInstance = MainWindow() # Create GUI class instance
g_timer = threading.Timer(TIMER_START_DELAY_SEC, print) # tmr inst to allow timer cancel when GUI closed
#-----------------------------------------------------------------------

# Method to execute timer every PERIOD_SEC seconds to sample DTH22 sensor
def periodicDth22Sample():
    global g_sampleCount, g_timer
    g_sampleCount = g_sampleCount + 1;
    
    # Sample DTH22 sensor
    humidity, temperature = sampleDth22()
    
    # If sensor data received, insert to DB and update GUI
    if humidity is not None and temperature is not None and humidity < 100:
        insertSensorData(temperature, humidity)
        g_mainWindowInstance.updateStatusLine('DB Update: Temp={0:0.1f}C  Humidity={1:0.1f}%' \
                                            .format(temperature, humidity))
        g_mainWindowInstance.latestTempReading = temperature
        g_mainWindowInstance.latestHumidReading = humidity
        g_mainWindowInstance.checkTempLimit()
        g_mainWindowInstance.checkHumidityLimit()
    else:
        g_mainWindowInstance.updateStatusLine('Failed to Read Sensor Data', True)
    
    # Trigger next timer if timer executed less than MAX_SAMPLE_COUNTS times.
    # Otherwise, report sensor sampling complete.
    if(g_sampleCount < MAX_SAMPLE_COUNTS):
        g_timer = threading.Timer(PERIOD_SEC, periodicDth22Sample)
        g_timer.start()
    else:
        g_mainWindowInstance.updateStatusLine('Sensor Sampling Complete.')
    
    return 0

#-----------------------------------------------------------------------
# Method to launch GUI
def startGui():
    g_mainWindowInstance.show()
    g_mainWindowInstance.updateStatusLine('Application Started')
    g_qtApp.exec_()

#-----------------------------------------------------------------------
def main(args):
    global g_timer

    # Initialize connection to mySQL DB and create/open table for sensor data
    initializeDatabase()

    # Start periodic sampling of sensor data with short delay
    # Delay allows GUI to start before first sample is captured
    g_timer = threading.Timer(TIMER_START_DELAY_SEC, periodicDth22Sample)
    g_timer.start()
    
    # Start GUI application
    startGui()
    
    # Cancel sensor sampling timer to allow app to close properly
    g_timer.cancel()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

