#!/usr/bin/python3

""" gui.py: User Interface to display/request timestamped sensor data

    TODO

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
import project1_gui
from db import *
from sensor import *

__author__ = "Brian Ibeling"

#-----------------------------------------------------------------------
# Class for project1 GUI
class MainWindow(QMainWindow, project1_gui.Ui_MainWindow):
    def __init__(self):
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

    def updateCurrentSensorData(self, text: str):
        self.CurrentSensorData.setText(text)
        # Clear italic font from user instruction to display sensor data
        myFont = QtGui.QFont()
        myFont.setItalic(False)
        self.CurrentSensorData.setFont(myFont)

    def updateStatusLine(self, text: str):
        self.StatusLine.setText(text)
        
    def updateTempLimitStatus(self, text: str):
        # Clear Italic font, set text
        myFont = QtGui.QFont()
        myFont.setItalic(False)
        self.TempLimitStatus.setFont(myFont)
        self.TempLimitStatus.setText(text)
    
    def updateHumidLimitStatus(self, text: str):
        # Clear Italic font, set text
        myFont = QtGui.QFont()
        myFont.setItalic(False)
        self.HumidLimitStatus.setFont(myFont)
        self.HumidLimitStatus.setText(text)

    def checkTempLimit(self):
        if self.latestTempReading is not None:
            if self.latestTempReading > self.TempLimitSpinBox.value():
                self.updateTempLimitStatus("Over Temp Limit")
            else:
                self.updateTempLimitStatus("Temp within limits")

    def checkHumidityLimit(self):
        if self.latestHumidReading is not None:
            if self.latestHumidReading > self.HumidLimitSpinBox.value():
                self.updateHumidLimitStatus("Over Humidity Limit")
            else:
                self.updateHumidLimitStatus("Humidity within limits")

    def buttonPressCurrData(self):
        # Sample DTH22 sensor, check temp/humidity upper limit
        humidity, temperature = sampleDth22()
        if humidity is not None and temperature is not None and humidity < 100:
            self.updateCurrentSensorData('Temp={0:0.1f}C  Humidity={1:0.1f}%'.format(temperature, humidity))
            self.latestTempReading = temperature
            self.latestHumidReading = humidity
            self.checkTempLimit()
            self.checkHumidityLimit()
        else:
            self.updateCurrentSensorData('Failed to Read Sensor Data')

    def buttonPressGraphTemp(self):
        # Get last N number of temperature samples captured in DB, data returned in arrays.
        timestamp, temp = getRecentTempData(10)

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

    def buttonPressGraphHumidity(self):
        # Get last N number of humidity samples captured in DB, data returned in arrays.
        timestamp, humidity = getRecentHumidityData(10)

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
