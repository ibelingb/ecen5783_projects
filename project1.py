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

"""

from sensor import sampleDth22

__author__ = "Brian Ibeling"

def main(args):
	
	
	sampleDth22();

	
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

