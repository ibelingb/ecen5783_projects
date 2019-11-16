#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 11/14/2019

""" camera.py: 
                  TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
      - https://projects.raspberrypi.org/en/projects/getting-started-with-picamera
      - https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/8
"""
__author__ = "Brian Ibeling"

import sys
from picamera import PiCamera
from time import sleep
from datetime import datetime

IMAGE_PATH = "/home/pi/repos/ecen5783_project/client_pi/"

piCamera = PiCamera()

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------
# Object Instances and Variables
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
def InitializeCamera():
  """
    Initialize and apply settings to camera
  """
  # Apply rotation to PiCamera as necessary based on hardware orientation/installation
  piCamera.rotation = 90
  piCamera.framerate = 15 # Max Framerate
  #piCamera.resolution = (800, 800) # Set image resolution
  return 0

#-----------------------------------------------------------------------
def CaptureImage():
  
  # Capture image using attached PiCamera
  print("Capturing image...")
  piCamera.start_preview()
  sleep(3) # Note: important sleep is at least 2 seconds to allow camera to sense light levels
  imageName = ("img_" + str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + ".jpg")
  piCamera.capture(IMAGE_PATH + imageName)
  piCamera.stop_preview()
  print("Image capture complete")

  # Return string to pi_client with captured image name
  # TODO
  # imageName

  return 0
#-----------------------------------------------------------------------
def main(args):

  # Initialize Camera
  InitializeCamera()

  # Capture image
  CaptureImage()

  return 0
#-----------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main(sys.argv))
