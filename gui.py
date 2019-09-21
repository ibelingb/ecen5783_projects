#!/usr/bin/python3

""" gui.py: User Interface to display/request timestamped sensor data

    TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://www.baldengineer.com/raspberry-pi-gui-tutorial.html
        - https://matplotlib.org/tutorials/introductory/pyplot.html
"""

import sys
import PyQt5
from PyQt5.QtWidgets import *

import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
import project1_gui
from db import *
from sensor import *

#-----------------------------------------------------------------------
# Class for project1 GUI
class MainWindow(QMainWindow, project1_gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Button press hooks
        self.ReadSensorButton.clicked.connect(lambda: self.buttonPressCurrData())
        self.GraphTempButton.clicked.connect(lambda: self.buttonPressGraphTemp())
        self.GraphHumidityButton.clicked.connect(lambda: self.buttonPressGraphHumidity())

    def updateCurrentSensorData(self, text: str):
        self.CurrentSensorData.setText(text)

    def updateStatusLine(self, text: str):
        self.StatusLine.setText(text)

    def buttonPressCurrData(self):
        # Sample DTH22 sensor
        humidity, temperature = sampleDth22()
        if humidity is not None and temperature is not None and humidity < 100:
            self.updateCurrentSensorData('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            self.updateCurrentSensorData('Failed to Read Sensor Data')

    def buttonPressGraphTemp(self):
        # Get last N number of temperature samples captured in DB, data returned in arrays.
        timestamp, temp = getRecentTempData(10)

        for value in timestamp:
            print(value)
        for value in temp:
            print(value)

        # Generate plot of last 10 values retrieved from DB - save as image
        plt.cla() # Clear plot to remove previous generated plot
        plt.plot(timestamp, temp)
        plt.title('Last 10 Samples DHT22 Temperature Samples')
        plt.ylabel('Temperature (deg C)')
        plt.xlabel('Timestamp')
        plt.grid(True)
        plt.savefig("temp_graph.png")
        
        # Display saved plot image
        graph = QLabel(self.GraphLabel)
        graph.clear()
        graph.setPixmap(QPixmap("temp_graph.png"))
        graph.show()
        self.GraphLabel.resize(800, 600)
        
        return 0

    def buttonPressGraphHumidity(self):
        # Get last N number of humidity samples captured in DB, data returned in arrays.
        timestamp, humidity = getRecentHumidityData(10)
        
        for value in timestamp:
            print(value)
        for value in humidity:
            print(value)

        # Generate plot of last 10 values retrieved from DB - save as image
        plt.cla() # Clear plot to remove previous generated plot
        plt.plot(timestamp, humidity)
        plt.title('Last 10 Samples DHT22 Humidity Samples')
        plt.ylabel('Humidity (%)')
        plt.xlabel('Timestamp')
        plt.grid(True)
        plt.savefig("humidity_graph.png")
        
        # Display saved plot image
        graph = QLabel(self.GraphLabel)
        graph.clear()
        graph.setPixmap(QPixmap("humidity_graph.png"))
        graph.show()
        self.GraphLabel.resize(800, 600)
        
        return 0

#-----------------------------------------------------------------------
