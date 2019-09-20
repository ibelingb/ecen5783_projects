#!/usr/bin/python3

""" gui.py: User Interface to display/request timestamped sensor data

    TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://www.baldengineer.com/raspberry-pi-gui-tutorial.html
        
"""

import sys
import PyQt5
from PyQt5.QtWidgets import *
import project1_gui
from db import *
from sensor import *

# Class for project1 GUI
class MainWindow(QMainWindow, project1_gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Button press hooks
        self.pushButton.clicked.connect(lambda: self.buttonPressCurrData())
        
    def buttonPressCurrData(self):
        print("Print Current Data")

# Method to launch GUI
def startGui():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
    
    
