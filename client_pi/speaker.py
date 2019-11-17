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
"""

__author__ = "Brian Ibeling"

import sys
from time import sleep
from pygame import mixer

DIR = "/home/pi/repos/ecen5783_project/client_pi/"

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------
# Object Instances and Variables
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
def InitializeSpeaker():
  """
      TOOD
  """
  mixer.init() #turn all of pygame on.

  return 0

#-----------------------------------------------------------------------
def main(args):

  InitializeSpeaker()

  sound = mixer.Sound(DIR + 'receivedAudio.wav')
  sound.play()
  sleep(3) # Delay while audio file is played

  return 0
#-----------------------------------------------------------------------
if __name__ == '__main__':
  sys.exit(main(sys.argv))
