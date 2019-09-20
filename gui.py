#!/usr/bin/python3

""" gui.py: User Interface to display/request timestamped sensor data

    TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - 
        
"""

import sys
import PyQt5
from PyQt5.QtWidgets import *
import project1_gui

# Class for project1 GUI
class MainWindow(QMainWindow, project1_gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

def startGui():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
