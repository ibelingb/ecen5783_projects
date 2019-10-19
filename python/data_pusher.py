#!/usr/bin/python3
#
# ECEN5783
# Author: Brian Ibeling
# 10/19/2019

""" data_pusher.py: Python interface between the Python GUI and AWS to pass sensor sample and 
                    alert events to AWS IoT.
                

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html
        - https://techblog.calvinboey.com/raspberrypi-aws-iot-python/
"""

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

__author__ = "Brian Ibeling"

myMQTTClient = AWSIoTMQTTClient("RpiClient")

#-----------------------------------------------------------------------
def initializeDataPusher():
  # Establish AWS IoT certificate based connection
  myMQTTClient.configureEndpoint("a376p1vo77mjsi-ats.iot.us-east-1.amazonaws.com", 8883)
  myMQTTClient.configureCredentials("/home/pi/certs/Amazon_Root_CA_1.pem", "/home/pi/certs/0b8296d0dd-private.pem.key", "/home/pi/certs/0b8296d0dd-certificate.pem.crt")
  myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
  myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
  myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
  myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

  return 0
#-----------------------------------------------------------------------
def pushDataToAws(sensorData):
  # Connect and publish data packet
  myMQTTClient.connect()
  myMQTTClient.publish("sensor/data", str(sensorData), 0)

  return 0
#-----------------------------------------------------------------------
def pushAlertToAws(alertData):
  # Connect and publish alert packet
  myMQTTClient.connect()
  myMQTTClient.publish("sensor/alert", str(alertData), 0)

  return 0
#-----------------------------------------------------------------------
