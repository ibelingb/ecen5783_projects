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
      - https://docs.aws.amazon.com/code-samples/latest/catalog/python-sqs-send_message.py.html
      - https://boto4.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html
      - https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-python.html

    + AWS Credentials Setup +
    Credentials setup to pass data files to AWS S3 found by going to:
      AWS Starter Account >> Vocareum >> Account Details button >> AWS CLI Dropdown
    Then, Copy-Paste the info under [default] to ~/.aws/credentials
"""

__author__ = "Brian Ibeling"

import sys
import time
import boto3
import json

#from camera import *
#from microphone import *
#from speaker import *

#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# Constants
S3_AUDIO_BUCKET = "magicwandaudiobucket" # S3 Bucket name
S3_IMAGE_BUCKET = "magicwandimagebucket" # S3 Bucket name
S3_TRANSCRIBE_BUCKET = "magicwandtranscribedaudio" # S3 Bucket name
S3_IMAGE_BUCKET_URL = "https://magicwandimagebucket.s3.amazonaws.com/"
SQS_URL = "https://sqs.us-east-1.amazonaws.com/582548553336/magicWandQueue"

audioFile = "recordedAudio_11212019-181859.wav"
imageFile = "img_11212019-181819.jpg"

#-----------------------------------------------------------------------
# Object Instances and Variables
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
rekognition = boto3.client('rekognition')
polly = boto3.client('polly')
sqs = boto3.client('sqs')

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
def triggerTranscribeJob(audioFilename):

  response = transcribe.start_transcription_job(
    TranscriptionJobName = audioFilename,
    LanguageCode = "en-US",
    MediaSampleRateHertz = 44100,
    MediaFormat = "wav",
    Media = {"MediaFileUri": "https://magicwandaudiobucket.s3.amazonaws.com/" + audioFilename},
    OutputBucketName = "magicwandtranscribedaudio")

#-----------------------------------------------------------------------
def getTranscribedAudio(jobName):
  # Loop until transcribe job is completed
  while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=audioFile)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED']:
      break
    elif status['TranscriptionJob']['TranscriptionJobStatus'] in ['FAILED']:
      print("Transcribe job " + jobName + " failed")
      return -1 
    sleep(1)

  # Get transcribed text from audio file
  fileObj = s3.get_object(Bucket=S3_TRANSCRIBE_BUCKET, Key=jobName+".json")
  fileData = fileObj['Body'].read()
  transcribedAudioStr = fileData.decode('utf-8')
  transcribedAudioJson = json.loads(transcribedAudioStr)
  transcribedAudio = transcribedAudioJson["results"]["transcripts"][0]["transcript"]

  print(transcribedAudio)

  return 0

#-----------------------------------------------------------------------
def parseLabelResponse(rekogResponse):
  label = None

  # Replace single quote with double quotes
  rekogResponse = rekogResponse.replace("\'", "\"")

  jsonData = json.loads(rekogResponse)

  # Parse receieved JSON for highest % guess and return label
  data = jsonData["Labels"][0]["Name"]

  return label
#-----------------------------------------------------------------------
def sqsWriteImageLink(imageFilename):
  # Populate JSON object with image link
  jsonData = '{  "recordType": "imageLink"' \
             ',  "link": "'+ str(S3_IMAGE_BUCKET_URL + imageFilename) + '"}'

  # Write to SQS
  msg = sqs.send_message(QueueUrl=SQS_URL,
                         MessageBody=jsonData)
  return 0
#-----------------------------------------------------------------------
def sqsWriteLabel(imageFilename, label):
  # Populate JSON object with image label info
  jsonData = '{  "recordType": "imageLabel"' \
             ',  "image": "' + imageFilename + \
             ',  "label": "' + label + '"}'

  # Write to SQS
  msg = sqs.send_message(QueueUrl=SQS_URL,
                         MessageBody=jsonData)
#-----------------------------------------------------------------------
def sqsWriteImageTag(imageFilename, tag):
  # Verify if image tag is provided
  # Image Tag can be unknown if no response in provided from user
  if(tag != "correct" or tag != "incorrect"):
    tag = "unknown"

  # Populate JSON object with image tag (correct or incorrect) info
  jsonData = '{  "recordType": "imageTag"' \
             ',  "image": "' + imageFilename + \
             ',  "tag": "' + tag + '"}'

  # Write to SQS
  msg = sqs.send_message(QueueUrl=SQS_URL,
                         MessageBody=jsonData)
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

  # Send image link to SQS
  sqsWriteImageLink(imageFile)

  # Trigger AWS Transcribe to process audio file
#triggerTranscribeJob(audioFile)

  # Get text from AWS Transcribe job
  getTranscribedAudio(audioFile)

  # Trigger AWS Rekognition to process image file and print resulting analysis
  response = rekognition.detect_labels(Image={'S3Object':{'Bucket':S3_IMAGE_BUCKET,'Name':imageFile}},MaxLabels=10)
  print(response)
  # Send label info to SQS
  label = parseLabelResponse(str(response))
  sqsWriteLabel(imageFile, str(label))

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
