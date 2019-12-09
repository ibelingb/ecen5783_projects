#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 11/14/2019

""" speaker.py: 
                  TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
      - https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-2-play-sounds
      - https://stackoverflow.com/questions/14845896/pygame-cannot-open-sound-file
      - https://stackoverflow.com/questions/34668981/pygame-unable-to-open-mp3-file
"""

__author__ = "Brian Ibeling"

import sys
import time
from pygame import mixer
import zmq

OUTPUT_AUDIO_DIR = "/home/pi/repos/ecen5783_project/client_pi/output_audio/"

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------
# Object Instances and Variables
#-----------------------------------------------------------------------
context = zmq.Context()
speakerSocket = context.socket(zmq.SUB)
speakerSocket.setsockopt_string(zmq.SUBSCRIBE, "speak")
speakerSocket.connect("tcp://127.0.0.1:6004")
#-----------------------------------------------------------------------
def InitializeSpeaker():
  """
      TOOD
  """
  mixer.init() #turn all of pygame on.

  return 0

#-----------------------------------------------------------------------
def main(args):
  """
      TOOD
  """
  outputAudio = ""

  print("Launching speaker.py")


  while True:
    try:
      # Receive signal from client_pi process
      outputAudio = speakerSocket.recv_string(flags=zmq.NOBLOCK)

      if(outputAudio == "speak"):
        print("Output Audio signal received")

        #InitializeSpeaker()

        # Output audio
        sound = mixer.music.load(OUTPUT_AUDIO_DIR + 'sound.mp3')
        sound = mixer.music.play()
        time.sleep(3) # Delay while audio file is played
        sound = mixer.music.stop()

        # Clear flag
        outputAudio = ""

    except zmq.Again as e:
      # speaker signal not received
      outputAudio = ""

  return 0
#-----------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main(sys.argv))
