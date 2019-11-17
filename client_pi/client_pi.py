#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 11/14/2019

""" client_pi.py: Main python file for EID SuperProject Client Pi to handle embedded devices for 
                  the Magic Wand Superproject.
                  TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
      - https://docs.aws.amazon.com/code-samples/latest/catalog/python-s3-s3-python-example-upload-file.py.html
      - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
      - 

    + AWS Credentials Setup +
    Credentials setup to pass data files to AWS S3 found by going to:
      AWS Starter Account >> Vocareum >> Account Details button >> AWS CLI Dropdown
    Then, Copy-Paste the info under [default] to ~/.aws/credentials
"""

__author__ = "Brian Ibeling"

import sys
import time
import boto3

#from camera import *
#from microphone import *
#from speaker import *

#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# Constants
S3_AUDIO_BUCKET = "magicwandaudiobucket" # S3 Bucket name
S3_IMAGE_BUCKET = "magicwandimagebucket" # S3 Bucket name

#-----------------------------------------------------------------------
# Object Instances and Variables
s3 = boto3.client('s3')

#-----------------------------------------------------------------------
def pushAudioToAws(audioFilename):

  # Send audio to AWS S3 audio Bucket
  s3.upload_file(audioFilename, S3_AUDIO_BUCKET, audioFilename)

  return 0
#-----------------------------------------------------------------------
def pushImageToAws(imageFilename):

  # Send audio to AWS S3 audio Bucket
  s3.upload_file(imageFilename, S3_IMAGE_BUCKET, imageFilename)

  return 0
#-----------------------------------------------------------------------
def main(args):
  """ Main for SuperProject Client_Pi - 
      TOOD
  """

  # Testing AWS connection
  pushAudioToAws("recordedAudio_11162019-164619.wav")
  pushImageToAws("img_11172019-131621.jpg")

  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
