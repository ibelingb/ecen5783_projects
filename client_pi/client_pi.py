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
      - https://pypi.org/project/boto3/
      - https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html
      - https://docs.aws.amazon.com/polly/latest/dg/get-started-what-next.html
      - https://medium.com/@julsimon/amazon-polly-hello-world-literally-812de2c620f4

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

audioFile = "recordedAudio_11202019-190712.wav"
imageFile = "img_11202019-184011.jpg"

#-----------------------------------------------------------------------
# Object Instances and Variables
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
polly = boto3.client('polly')

#-----------------------------------------------------------------------
def pushAudioToAws(audioFilename):
  # Verify audio file exists
  # TODO

  # Send audio to AWS S3 audio Bucket
  s3.upload_file(audioFilename, S3_AUDIO_BUCKET, audioFilename)

  return 0
#-----------------------------------------------------------------------
def pushImageToAws(imageFilename):
  # Verify image file exists
  # TODO

  # Send audio to AWS S3 audio Bucket
  s3.upload_file(imageFilename, S3_IMAGE_BUCKET, imageFilename)

  return 0
#-----------------------------------------------------------------------
def main(args):
  """ Main for SuperProject Client_Pi - 
      TOOD
  """
  ### Testing of AWS functionality ###
  # Send data to AWS S3 Buckets
  pushAudioToAws(audioFile)
  pushImageToAws(imageFile)

  # Trigger AWS Transcribe to process audio file
  # TODO

  # Trigger AWS Rekognition to process image file and print resulting analysis
  response = rekognition.detect_labels(Image={'S3Object':{'Bucket':S3_IMAGE_BUCKET,'Name':imageFile}},MaxLabels=10)
  print(response)

  # Determine which name has highest confident score from AWS Rekognition, pass to AWS Polly
  # Request speech synthesis and output mp3 into file
  response = polly.synthesize_speech(Text=str(response), OutputFormat="mp3", VoiceId="Joanna")
  print(response)
  soundfile = open('/tmp/sound.mp3', 'wb')
  soundBytes = response['AudioStream'].read()
  soundfile.write(soundBytes)
  soundfile.close()

  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
