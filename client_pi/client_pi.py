#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 11/14/2019

""" client_pi.py: Main python file for EID SuperProject Client Pi to handle embedded devices for 
                  the Magic Wand Superproject. This client_pi acts as the main controller for
                  embedded peripherals and acts as the intermediary to all AWS components. 

                  Data is passed between various software components using Zero Message Queue in
                  a PubSub configuration. This allows data to be pushed between python processes
                  without needing a response from the receiving process and allows messages/data/signals
                  to be queued up.

                  Main loops begins by receiving audio filenames from the microphone_speaker.py process.
                  As filenames are received, they're passed to AWS Transcribe to be converted to text. Based
                  on the text received, an action will be taken if the "identifio/correcto/wrongo" command 
                  is recognized. Then an image is captured, sent to AWS Rekognition and the image is then 
                  saved to AWS S3 to be accessed by the server_pi application.

                  Data to the Server webpage is done via MQTT with AWS IoT Core. Data fed to this is then passed
                  to the shared SQS between the client_pi and server_pi, which is then processed and served onto
                  the server_pi webpage.
                  

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
      - https://www.digitalocean.com/community/tutorials/how-to-work-with-the-zeromq-messaging-library

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
import zmq
import base64
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#-----------------------------------------------------------------------
# Constants
S3_AUDIO_BUCKET = "magicwandaudiobucket" # S3 Bucket name
S3_IMAGE_BUCKET = "magicwandimagebucket" # S3 Bucket name
S3_TRANSCRIBE_BUCKET = "magicwandtranscribedaudio" # S3 Bucket name
S3_IMAGE_BUCKET_URL = "https://magicwandimagebucket.s3.amazonaws.com/"
SQS_URL = "https://sqs.us-east-1.amazonaws.com/582548553336/magicWandQueue"
AUDIOFILE_DIR = "/home/pi/repos/ecen5783_project/client_pi/audio_files/"
IMAGEFILE_DIR = "/home/pi/repos/ecen5783_project/client_pi/image_files/"
OUTPUT_AUDIO_DIR = "/home/pi/repos/ecen5783_project/client_pi/output_audio/"

# Define ZMQ socket connections
context = zmq.Context()
recordSocket = context.socket(zmq.SUB)
recordSocket.setsockopt_string(zmq.SUBSCRIBE, "recorded")
recordSocket.connect("tcp://127.0.0.1:6001")
takePicSocket = context.socket(zmq.PUB)
takePicSocket.bind("tcp://127.0.0.1:6002")
imageSocket = context.socket(zmq.SUB)
imageSocket.setsockopt_string(zmq.SUBSCRIBE, "img")
imageSocket.connect("tcp://127.0.0.1:6003")
speakerSocket = context.socket(zmq.PUB)
speakerSocket.bind("tcp://127.0.0.1:6004")

# Define AWS IoT connection client
myMQTTClient = AWSIoTMQTTClient("RpiClient")

#-----------------------------------------------------------------------
# Object Instances and Variables
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
rekognition = boto3.client('rekognition')
polly = boto3.client('polly')
sqs = boto3.client('sqs')

# Define array to keep track of audio files sent to Transcribe AWS service
audioTranscribeArray = []

# Image Filename used to determine image tag received from user (correct vs incorrect)
imageFile = None

#-----------------------------------------------------------------------
# client_pi Methods
#-----------------------------------------------------------------------
def initAwsIotConnection():
  # Establish AWS IoT certificate based connection
  myMQTTClient.configureEndpoint("a376p1vo77mjsi-ats.iot.us-east-1.amazonaws.com", 8883)
  myMQTTClient.configureCredentials("/home/pi/certs/Amazon_Root_CA_1.pem", "/home/pi/certs/0b8296d0dd-private.pem.key", "/home/pi/certs/0b8296d0dd-certificate.pem.crt")
  myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
  myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
  myMQTTClient.configureConnectDisconnectTimeout(300)  # sec
  myMQTTClient.configureMQTTOperationTimeout(300)  # sec
  myMQTTClient.connect()

  return 0
#-----------------------------------------------------------------------
def pushAudioToAws(audioFilename):
  # Send audio to AWS S3 audio Bucket
  s3.upload_file(AUDIOFILE_DIR + audioFilename, S3_AUDIO_BUCKET, audioFilename)

  return 0
#-----------------------------------------------------------------------
def pushImageToAws(imageFilename):
  # Convert image to base64 so it plays nice with API Gateway on server_pi end
  with open(IMAGEFILE_DIR + "base64" + imageFilename, "wb") as fout:
    with open(IMAGEFILE_DIR + imageFilename, "rb") as fin:
      fout.write(base64.b64encode(fin.read()))

  # Send both original and base64 images to AWS S3 image Bucket
  s3.upload_file(IMAGEFILE_DIR + "base64" + imageFilename, S3_IMAGE_BUCKET, "b64_" + imageFilename)
  s3.upload_file(IMAGEFILE_DIR + imageFilename, S3_IMAGE_BUCKET, imageFilename)

  # Delete base64 version of image
  os.remove(IMAGEFILE_DIR + "base64" + imageFilename)

  return 0

#-----------------------------------------------------------------------
def triggerTranscribeJob(audioFilename):
  # Kick off an AWS Transcribe job with the received Audio File
  response = transcribe.start_transcription_job(
    TranscriptionJobName = audioFilename,
    LanguageCode = "en-US",
    MediaSampleRateHertz = 44100,
    MediaFormat = "wav",
    Media = {"MediaFileUri": "https://magicwandaudiobucket.s3.amazonaws.com/" + audioFilename},
    Settings = {"VocabularyName": "magicWandCmdVocab"},
    OutputBucketName = "magicwandtranscribedaudio")

#-----------------------------------------------------------------------
def getTranscribedAudio(jobName):
  # Read current job status from AWS Transcribe
  status = transcribe.get_transcription_job(TranscriptionJobName=jobName)
  if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED']:
    # Get transcribed text from audio file
    fileObj = s3.get_object(Bucket=S3_TRANSCRIBE_BUCKET, Key=jobName+".json")
    fileData = fileObj['Body'].read()
    transcribedAudioStr = fileData.decode('utf-8')
    transcribedAudioJson = json.loads(transcribedAudioStr)
    transcribedAudio = transcribedAudioJson["results"]["transcripts"][0]["transcript"]

    # Audiofile processed, pop first element from transcript array
    print("Transcribe job " + jobName + " complete")
    audioTranscribeArray.pop(0)

    return transcribedAudio
  elif status['TranscriptionJob']['TranscriptionJobStatus'] in ['FAILED']:
    # Transcribe job failed to complete successfully, remove audiofile from processing list
    print("Transcribe job " + jobName + " failed")
    audioTranscribeArray.pop(0)
    return -1
  else:
    # Transcribe job still in progress
    return -1

#-----------------------------------------------------------------------
def handleCommand(cmd):
  # Handle the various voice commands available to the client_pi system
  global imageFile

  # If no command received from user audio, ignore message
  if(cmd == ""):
    return None

  print("Translated Audio received " + cmd)

  # Determine if actionable command received
  if("identifio" in cmd):
    # Capture image
    print("Identifio cmd received")
    sqsWriteCmdRecognized(True)
    return "identifio"
  elif("correcto" in cmd):
    # Image label correct
    print("Correcto cmd received")
    sqsWriteCmdRecognized(True)
    if(imageFile != None):
      sqsWriteImageTag(imageFile, "correct")
    imageFile = None
    return "correcto"
  elif("wrongo" in cmd):
    # Image label incorrect
    print("wrongo cmd received")
    sqsWriteCmdRecognized(True)
    if(imageFile != None):
      sqsWriteImageTag(imageFile, "incorrect")
    imageFile = None
    return "wrongo"
  else:
    # No command recognized
    sqsWriteCmdRecognized(False)
    return None

#-----------------------------------------------------------------------
def parseLabelResponse(rekogResponse):
  label = None

  # Replace single quote with double quotes
  rekogResponse = rekogResponse.replace("\'", "\"")

  jsonData = json.loads(rekogResponse)

  # Parse receieved JSON for highest % guess and return label
  label = jsonData["Labels"][0]["Name"]

  return label
#-----------------------------------------------------------------------
def sqsWriteImageLink(imageFilename):
  # Populate JSON object with image link
  jsonData = '{  "recordType": "imageLink"' \
             ',  "link": "'+ str(S3_IMAGE_BUCKET_URL + imageFilename) + '"}'

  # Write to SQS via IoT
  myMQTTClient.publish("clientPi/imageLink", str(jsonData), 0)

  return 0
#-----------------------------------------------------------------------
def sqsWriteLabel(imageFilename, label):
  # Populate JSON object with image label info
  jsonData = '{  "recordType": "imageLabel"' \
             ',  "image": "' + imageFilename + '"'\
             ',  "label": "' + label + '"}'

  # Write to SQS via IoT
  myMQTTClient.publish("clientPi/imageLabel", str(jsonData), 0)

  return 0
#-----------------------------------------------------------------------
def sqsWriteImageTag(imageFilename, tag):
  # Verify if image tag is provided
  # Image Tag can be unknown if no response in provided from user
  if not ("correct" or "incorrect") in tag:
    tag = "unknown"

  # Populate JSON object with image tag (correct or incorrect) info
  jsonData = '{  "recordType": "imageTag"' \
             ',  "image": "' + imageFilename + '"'\
             ',  "tag": "' + tag + '"}'

  # Write to SQS via IoT
  myMQTTClient.publish("clientPi/imageTag", str(jsonData), 0)

  return 0
#-----------------------------------------------------------------------
def sqsWriteCmdRecognized(isRecognized):
  # Populate JSON object with image label info
  jsonData = '{  "recordType": "cmdRecognized"' \
             ',  "cmdRecognized": "' + str(isRecognized) + '"}'

  # Write to SQS via IoT
  myMQTTClient.publish("clientPi/cmdRecognized", str(jsonData), 0)

  return 0
#-----------------------------------------------------------------------
def main(args):
  """ Main for SuperProject Client_Pi - 
      TOOD
  """
  global audioFile
  global imageFile

  # Establish connection with AWS IoT
  initAwsIotConnection()
 
  # Main loop to continuously run
  while True:
    awaitingIdCmd = True
  
    # Loop until identifio command received from user
    # Also send any received audio files to AWS Transcribe to be processed
    # Then monitor the earliest process sent from audioTranscribeArray[] to determine 
    # actions needed in order they're received
    while (awaitingIdCmd):
      # Receive audioFilename from microphone process
      try:
        # Receive audioFilename from microphone process
        audioFile = recordSocket.recv_string(flags=zmq.NOBLOCK)
    
        # Send data to AWS S3 Buckets
        pushAudioToAws(audioFile)
        print("Received Audiofile " + audioFile)

        # Trigger AWS Transcribe to process audio file
        print("triggerTranscribeJob")
        triggerTranscribeJob(audioFile)

        # Add to Array to track transcribe jobs
        audioTranscribeArray.append(audioFile)
  
      except zmq.Again as e:
        # recorded audio not yet available, no action needed
        temp = ""

      # Get status and transcribed text from top of AWS Transcribe job queue
      if(len(audioTranscribeArray) > 0):
        command = getTranscribedAudio(str(audioTranscribeArray[0]))
       
        # Continue if any audio received
        if(command != -1):
          # Audio received; Determine if recognizable command received from user
          print("handleCommand")
          receivedCmd = handleCommand(command)
          
          # Primary command trigger received - capture image and associated metadata
          if(receivedCmd == "identifio"):
            awaitingIdCmd = False

      time.sleep(1)
  
    # Trigger image to be captured by camera.py process
    print("Send takePic signal")
    takePicSocket.send_string("takePic")
  
    # Receive imageFilename from camera process
    while True:
      try:
        # Receive imageFilename from camera process
        imageFile = imageSocket.recv_string(flags=zmq.NOBLOCK)
        print("Received imageFile " + imageFile)
        break
      except zmq.Again as e:
        # image not yet available
        imageFile = ""
 
    # Send image to AWS S3 bucket for server_pi to access
    print("pushImageToAws")
    pushImageToAws(imageFile)
  
    # Send image link to SQS for server_pi to access
    print("sqsWriteImageLink")
    sqsWriteImageLink(imageFile)
  
    # Trigger AWS Rekognition to process image file and print resulting analysis
    response = rekognition.detect_labels(Image={'S3Object':{'Bucket':S3_IMAGE_BUCKET,'Name':imageFile}},MaxLabels=5)
    print(response)
    # Send label info to SQS
    label = parseLabelResponse(str(response))
    sqsWriteLabel(imageFile, str(label))
  
    # Determine which name has highest confident score from AWS Rekognition, pass to AWS Polly
    # Request speech synthesis and output mp3 into file
    print("sendToPolly")
    response = polly.synthesize_speech(Text=str(label), OutputFormat="mp3", VoiceId="Joanna")
    # Writing capturing sound file to filesystem for speaker process to access
    print("writeOutputAudioFile")
    soundfile = open(OUTPUT_AUDIO_DIR + 'sound.mp3', 'wb')
    soundBytes = response['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.flush()
    soundfile.close()

    # Signal to speaker to output returned label in sound.mp3 file
    print("sendSpeakerSignal")
    speakerSocket.send_string("speak")

  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
