#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling and Connor Shapiro
# 10/14/2019

""" project3.py: Main python file for EID Project3 to store and display DHT22 data in a QT GUI,
                 and run a webserver exposing this data via WebSockets.

    Main python application to launch the GUI, create/connect to the database sensors table and
    provide all the necessary user interactions via the GUI. Also starts a timer when the program
    is launched to sample DTH22 sensor data every PERIOD_SEC (default 15), storing that into the 
    sensors database. When the GUI application is closed, the timer is cancelled.

    The Qt GUI is run with the PEP 3156 (asyncio standard) Event-Loop thanks to the quamash module.
    By running Qt in the asyncio event loop instead of the usual Qt loop, a Tornado webserver may
    run concurrently without the need for threading/multiprocessing.

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://github.com/adafruit/Adafruit_Python_DHT
        - https://docs.python.org/2/library/threading.html
"""

import sys
import time
import threading
import asyncio
from db import *
from sensor import *
from gui import *
from quamash import QEventLoop, QThreadExecutor
import webserver

__author__ = "Brian Ibeling & Connor Shapiro"

#-----------------------------------------------------------------------
# Constants
PERIOD_SEC = 15 # Time (in seconds) to periodically sample sensor data
TIMER_START_DELAY_SEC = 3 # Delay for sensor sample timer to allow GUI to start before first sample
MAX_SAMPLE_COUNTS = 30 # Max number of sensor samples to capture from timer firing
#-----------------------------------------------------------------------
# Object Instances and Variables
g_sampleCount = 0 # Variable to track number of data sample executions
g_qtApp = QApplication(sys.argv) # Start QT Application
g_mainWindowInstance = MainWindow() # Create GUI class instance
g_timer = threading.Timer(TIMER_START_DELAY_SEC, print) # tmr inst to allow timer cancel when GUI closed
#-----------------------------------------------------------------------

def periodicDth22Sample():
  """ Method to execute the timer every PERIOD_SEC seconds to sample the DTH22 sensor.
      Timer will expire after MAX_SAMPLE_COUNTS have occurred.
  """
  global g_sampleCount, g_timer
  
  # Sample DTH22 sensor
  humidity, temperature = sampleDth22()
  
  # If sensor data received, insert to DB and update GUI
  if humidity is not None and temperature is not None and humidity < 100:
    g_sampleCount += 1
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
  """ Launch the main application GUI and update the status line to specify app has started. """
  g_mainWindowInstance.show()
  g_mainWindowInstance.updateStatusLine('Application Started')
  
  '''
  Instead of calling g_qtApp.exec_() we now use the QEventLoop from quamash,
  which allows Tornado and Qt to run concurrently through asyncio.
  '''
  loop = QEventLoop(g_qtApp)  # instantiate the loop
  asyncio.set_event_loop(loop)  # register loop with asyncio
  webserver.start_webserver()  # webserver.py will start the loop

  with loop:
    loop.run_forever()  # run_forever() for ease of coding, as we are just
                        # killing python with the stopApp.sh script when 
                        # finished with the application.

#-----------------------------------------------------------------------
def main(args):
  """ Main for project1 GUI and sensor application.
      This will initialize/connect to the project1 database, start the sensor sampling timer,
      and launch the GUI application for the user to view sampled timer data, request the
      current sensor data, graph the 10 latest temp and humidity samples, and set alarm limits
      for both sensors. The timer will expire after 30 samples, and will be cancelled if the GUI
      is closed.
  """
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