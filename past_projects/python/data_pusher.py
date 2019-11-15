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
        - https://zeromq.org/languages/python/
        - https://pyzmq.readthedocs.io/en/latest/unicode.html
        - https://stackoverflow.com/questions/26012132/zero-mq-socket-recv-call-is-blocking
"""

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import zmq
import time

__author__ = "Brian Ibeling"

#-----------------------------------------------------------------------
# Define AWS IoT connection client
myMQTTClient = AWSIoTMQTTClient("RpiClient")

# Define ZMQ sockets for receiving data and alert messages from GUI App
context = zmq.Context()
dataSocket = context.socket(zmq.REP)
dataSocket.bind("tcp://*:5555")
alertSocket = context.socket(zmq.REP)
alertSocket.bind("tcp://*:5556")
#-----------------------------------------------------------------------
def initializeDataPusher():
  global myMQTTClient

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
def pushDataToAws(sensorData):
  global myMQTTClient

  # Publish data packet to AWS IoT instance
  myMQTTClient.publish("sensor/data", str(sensorData), 0)

  return 0
#-----------------------------------------------------------------------
def pushAlertToAws(alertData):
  global myMQTTClient

  # Publish alert packet to AWS IoT instance
  myMQTTClient.publish("sensor/alert", str(alertData), 0)

  return 0
#-----------------------------------------------------------------------
def main():
  global dataSocket
  global alertSocket

  initializeDataPusher()

  # Loop to receive Data and Alert messages from GUI App and pass along to AWS IoT
  # ZMQ requires cmd/response, send_string required for each recv_string
  while True:
    # Define non-blocking dataSocket instance, pass recv Data msgs to AWS IoT
    try:
      message = dataSocket.recv_string(flags=zmq.NOBLOCK)
      pushDataToAws(message)
      dataSocket.send_string("Recv Data msg")
    except zmq.Again as e:
      # No data received on socket
      message=""

    # Define non-blocking alertSocket instance, pass recv Alert msgs to AWS IoT
    try:
      message = alertSocket.recv_string(flags=zmq.NOBLOCK)
      pushAlertToAws(message)
      alertSocket.send_string("Recv Alert msg")
    except zmq.Again as e:
      # No data received on socket
      message=""

  return 0

#-----------------------------------------------------------------------
# Launch data_pusher as separate python execution from GUI App
if __name__ == "__main__":
  main()
