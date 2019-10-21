#!/usr/bin/python3

""" gui.py: User Interface to display/request timestamped sensor data

    GUI interface which utilizes the generated PyQt interface to display temperature and 
    humidity data samples directly from the DTH22 device, as well as read from the MySQL
    sensors database.

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://www.baldengineer.com/raspberry-pi-gui-tutorial.html
        - https://matplotlib.org/tutorials/introductory/pyplot.html
        - https://stackoverflow.com/questions/4090383/plotting-unix-timestamps-in-matplotlib
        - https://www.tutorialspoint.com/pyqt/pyqt_qspinbox_widget.htm
"""

import sys
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as md
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime
import json
import project1_gui
from db import *
from sensor import *
from data_pusher import pushAlertToAws

__author__ = "Brian Ibeling"

#-----------------------------------------------------------------------
# Class for project1 GUI
class MainWindow(QMainWindow, project1_gui.Ui_MainWindow):
    def __init__(self):
        """ Constructor for GUI Class object.
            Also creates the button and sensor limit input function call hooks.
        """
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.latestTempReading = None
        self.latestHumidReading = None
        
        # Temp/Humid Limit setting on-change callback functions
        self.TempLimitSpinBox.valueChanged.connect(self.checkTempLimit)
        self.HumidLimitSpinBox.valueChanged.connect(self.checkHumidityLimit)
        
        # Button press hooks
        self.ReadSensorButton.clicked.connect(lambda: self.buttonPressCurrData())
        self.GraphTempButton.clicked.connect(lambda: self.buttonPressGraphTemp())
        self.GraphHumidityButton.clicked.connect(lambda: self.buttonPressGraphHumidity())
#-----------------------------------------------------------------------
    def updateCurrentSensorData(self, text: str, error = False):
        """ Method to update the Current Sensor data string output text and color
            - text (str) : String to update field to.
            - error (Bool) : Error flag to indicate if displayed text should be highlighted red.
        """
        # Clear italic font from user instruction to display sensor data
        myFont = QtGui.QFont()
        myFont.setItalic(False)
        self.CurrentSensorData.setFont(myFont)
        
        # Set text color on error
        if error is True:
            self.CurrentSensorData.setStyleSheet('color: red')
        else:
            self.CurrentSensorData.setStyleSheet('color: none')
        
        self.CurrentSensorData.setText(text)
#-----------------------------------------------------------------------
    def updateStatusLine(self, text: str, error = False):
        """ Method to update the Sensor Timer status string output text and color
            - text (str) : String to update field to.
            - error (Bool) : Error flag to indicate if displayed text should be highlighted red.
        """
        # Set text color on error
        if error is True:
            self.StatusLine.setStyleSheet('color: red')
        else:
            self.StatusLine.setStyleSheet('color: none')
            
        self.StatusLine.setText(text)
#-----------------------------------------------------------------------
    def updateTempLimitStatus(self, text: str):
        """ Method to update the Temp Limit status string output text and color
            - text (str) : String to update field to.
            - error (Bool) : Flag to indicate if displayed text should be highlighted red.
        """
        # Clear Italic font, set text
        myFont = QtGui.QFont()
        myFont.setItalic(False)
        self.TempLimitStatus.setFont(myFont)
        
        self.TempLimitStatus.setText(text)
#-----------------------------------------------------------------------    
    def updateHumidLimitStatus(self, text: str):
        """ Method to update the Humidity Limit status string output text and color
            - text (str) : String to update field to.
            - error (Bool) : Flag to indicate if displayed text should be highlighted red.
        """
        # Clear Italic font, set text
        myFont = QtGui.QFont()
        myFont.setItalic(False)
        self.HumidLimitStatus.setFont(myFont)
        
        self.HumidLimitStatus.setText(text)
#-----------------------------------------------------------------------
    def checkTempLimit(self):
        """ Method to compare retrived temperature data against the user specified limit set.
            Will trigger each time new data is read from the sensor or if the temp limit is updated.
        """
        if self.latestTempReading is not None:
            # Compare latest temperature data captured against the temp limit set.
            if self.latestTempReading > self.TempLimitSpinBox.value():
                self.updateTempLimitStatus("Over Temp Limit")
                self.TempLimitStatus.setStyleSheet('color: red')
                return True;
            else:
                self.updateTempLimitStatus("Temp within limits")
                self.TempLimitStatus.setStyleSheet('color: green')
                return False;
#-----------------------------------------------------------------------
    def checkHumidityLimit(self):
        """ Method to compare retrived humidity data against the user specified limit set.
            Will trigger each time new data is read from the sensor or if the humidity limit is updated.
        """
        if self.latestHumidReading is not None:
            # Compare latest humidity data captured against the temp limit set.
            if self.latestHumidReading > self.HumidLimitSpinBox.value():
                self.updateHumidLimitStatus("Over Humidity Limit")
                self.HumidLimitStatus.setStyleSheet('color: red')
                return True;
            else:
                self.updateHumidLimitStatus("Humidity within limits")
                self.HumidLimitStatus.setStyleSheet('color: green')
                return False;
#-----------------------------------------------------------------------
    def checkSensorAlerts(self, tempAlert, humidityAlert):
      # Determine if alert message needs to be sent to AWS IoT service if either temp/humidity
      # sensor sample has triggered an alarm on the GUI
      if tempAlert is True or humidityAlert is True:
        # Populate JSON object and tx to AWS IoT
        sensorAlert = '{  "recordType": "alert"' \
                      ',  "timestamp": "'   + str(datetime.now()) + \
                      '", "tempAlertLevel": "' + str(round(self.latestTempReading,1)) + \
                      '", "tempTrigLevel": "' + str(round(self.TempLimitSpinBox.value(),0)) + \
                      '", "humidityAlertLevel": "' + str(round(self.latestHumidReading,1)) + \
                      '", "humidityTrigLevel": "' + str(round(self.HumidLimitSpinBox.value(),0)) + '"}'
        pushAlertToAws(sensorAlert)

#-----------------------------------------------------------------------
    def buttonPressCurrData(self):
        """ Hook for if the "Get Current Data" button is pressed by the user.
            Will read temperature and humidity data the from DTH22 device, checking limits for each 
            to determine if limit alarms are triggered.
            In the event sensor data fails to be read properly, display an error string.
        """
        # Sample DTH22 sensor, check temp/humidity upper limits and trigger AWS Alert if limited exceeded
        humidity, temperature = sampleDth22()
        if humidity is not None and temperature is not None and humidity < 100:
            self.updateCurrentSensorData('Temp={0:0.1f}C  Humidity={1:0.1f}%'.format(temperature, humidity))
            self.latestTempReading = temperature
            self.latestHumidReading = humidity
            tempAlert = self.checkTempLimit()
            humidityAlert = self.checkHumidityLimit()
            # Determine if Alert msg needs to be sent to AWS IoT app
            self.checkSensorAlerts(tempAlert, humidityAlert)
        else:
            self.updateCurrentSensorData('Failed to Read Sensor Data', True)
#-----------------------------------------------------------------------
    def buttonPressGraphTemp(self):
        """ Graph the 10 latest temperature entries from the sensors DB. """
        # Get last N number of temperature samples captured in DB, data returned in arrays.
        timestamp, temp = getRecentTempData(10)

        # Clear user help text on app startup
        self.GraphLabel.setText('')

        # Generate plot of last 10 values retrieved from DB - save as image
        plt.cla() # Clear plot to remove previous generated plot
        plt.plot(timestamp, temp)
        plt.title('Last 10 Samples DHT22 Temperature Sensor')
        plt.ylabel('Temperature (deg C)')
        plt.xlabel('Timestamp')
        plt.grid(True)  
        # Adjust X-axis timestamp to display fully
        plt.subplots_adjust(bottom=0.4)
        plt.xticks(rotation=90)
        plt.xticks(timestamp)
        ax=plt.gca()
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.savefig("temp_graph.png") # Save plot image
        
        # Display saved plot image
        graph = QLabel(self.GraphLabel)
        graph.clear()
        graph.setPixmap(QPixmap("temp_graph.png"))
        graph.show()
        self.GraphLabel.resize(1000, 1000)
        
        return 0
#-----------------------------------------------------------------------
    def buttonPressGraphHumidity(self):
        """ Graph the 10 latest temperature entries from the sensors DB. """
        # Get last N number of humidity samples captured in DB, data returned in arrays.
        timestamp, humidity = getRecentHumidityData(10)

        # Clear user help text on app startup
        self.GraphLabel.setText('')

        # Generate plot of last 10 values retrieved from DB - save as image
        plt.cla() # Clear plot to remove previous generated plot
        plt.plot(timestamp, humidity)
        plt.title('Last 10 Samples DHT22 Humidity Sensor')
        plt.ylabel('Humidity (%)')
        plt.xlabel('Timestamp')
        plt.grid(True)  
        # Adjust X-axis timestamp to display fully
        plt.subplots_adjust(bottom=0.4)
        plt.xticks(rotation=90)
        plt.xticks(timestamp)
        ax=plt.gca()
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.savefig("humidity_graph.png") # Save plot image
        
        # Display saved plot image
        graph = QLabel(self.GraphLabel)
        graph.clear()
        graph.setPixmap(QPixmap("humidity_graph.png"))
        graph.show()
        self.GraphLabel.resize(1000, 1000)
        
        return 0
#-----------------------------------------------------------------------
