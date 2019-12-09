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
      - https://stackoverflow.com/questions/3316882/how-do-i-get-a-string-format-of-the-current-date-time-in-python
"""
__author__ = "Brian Ibeling"

import sys
from picamera import PiCamera
import time
from datetime import datetime
import zmq

IMAGE_PATH = "/home/pi/repos/ecen5783_project/client_pi/image_files/"

# Define ZMQ socket for receiving imageCapture cmds and sending images to client_pi
context = zmq.Context()
takePicSocket = context.socket(zmq.SUB)
takePicSocket.setsockopt_string(zmq.SUBSCRIBE, "takePic")
takePicSocket.connect("tcp://127.0.0.1:6002")
imageSocket = context.socket(zmq.PUB)
imageSocket.bind("tcp://127.0.0.1:6003")

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
  piCamera.start_preview()
  time.sleep(3) # Note: important sleep is at least 2 seconds to allow camera to sense light levels
  imageName = ("img_" + str(datetime.now().strftime("%m%d%Y-%H%M%S")) + ".jpg")
  piCamera.capture(IMAGE_PATH + imageName)
  piCamera.stop_preview()

  return imageName
#-----------------------------------------------------------------------
def main(args):
  captureImage = ""

  print("Launching camera.py")

  # Initialize Camera
  InitializeCamera()

  # Loop awaiting cmd from client_pi to capture image
  while True:
    # Capture image if signal received from client_pi
    try:
      captureImage = takePicSocket.recv_string(flags=zmq.NOBLOCK)

      if(captureImage == "takePic"):
        print("takePic signal received")

        # Capture image
        imageName = CaptureImage()

        # Send image name to client_pi
        imageSocket.send_string(imageName)
        
        # Reset flag
        captureImage = ""

    except zmq.Again as e:
      # image not yet available
      captureImage = ""

  return 0
#-----------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main(sys.argv))
