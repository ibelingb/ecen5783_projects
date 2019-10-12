# ECEN5783
# Author: Connor Shapiro
# 10/7/2019

""" webserver.py: Tornado Webserver python application for EID Project2 to serve DHT22 readings on-demand via WebSockets

  This python module launches a Tornado webserver which waits for a WebSocket connection from a remote device.
  Once connected, the webserver waits for either an on-demand DHT22 sensor reading request,
  or an on-demand data request for the remote client to run a speed test.

  + Resources and Citations +
  The following resources were used to assist with development of this SW.
    - https://web.archive.org/web/20161020184649/http://www.iot-projects.com/index.php?id=websocket-a-simple-example
    - https://www.tornadoweb.org/en/stable/index.html
    - https://github.com/harvimt/quamash
"""

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import syslog
import json
import db
from sensor import *

__author__ = "Connor Shapiro"

MAX_RETRIES = 3

class WSHandler(tornado.websocket.WebSocketHandler):

  def open(self):
    syslog.syslog('WebSocket connection opened.')

  def on_message(self, message):
    syslog.syslog('Message received via WebSocket connection.')
    messageResponseRaw = {'cmdResponse': message}

    ''' Expect plaintext request messages from the HTML client.
        Handle these with an if/else block
    '''

    # Provide on-demand reading
    if ("getLatestDbData" == message):
      syslog.syslog('Sensor reading requested. Beginning sensor reading.')
      finishedReading = False
      retryCount = 0  # Track n of sensor readings (may need more than 1)
      sensorError = False

      # If reading is invalid, try again, up to MAX_RETRIES times
      while not finishedReading:
        humidity, temperature = sampleDth22()
        if humidity is not None and temperature is not None and humidity < 100:
          finishedReading = True
        if not finishedReading:
          retryCount += 1
          if (MAX_RETRIES == retryCount):
            finishedReading = True
            sensorError = True
      if sensorError:
        syslog.syslog('Sensor reading failed after ' + str(MAX_RETRIES) + 
                      ' attempts.')
        messageResponseRaw['error'] = 'sensorHardware'
        messageResponseRaw['numSensorSamples'] = 0
      else:
        syslog.syslog('Sensor reading succeeded.')
        messageResponseRaw['numSensorSamples'] = 1
        sensorSamples = [{'temperature': round(temperature, 1), 'humidity': round(humidity, 1)}]
        messageResponseRaw['sensorSamples'] = sensorSamples

    # Provide data for speed test
    elif ("getLast10Samples" == message):
      timestamp, temperature, humidity = db.getRecentSensorData(10)

      # Confirm all three arrays are equally filled
      if not ((len(timestamp) == len(temperature))
              and (len(timestamp) == len(humidity))):
        messageResponseRaw['error'] = 'badMySQLRetrieval'
        messageResponseRaw['numSensorSamples'] = 0

      else:
        numSensorSamples = len(timestamp)
        messageResponseRaw['numSensorSamples'] = numSensorSamples
        sensorSamples = []
        for i in range(numSensorSamples):
          sensorSamples.append({'timestamp': str(timestamp[i]),
                                'temperature': round(temperature[i], 1),
                                'humidity': round(humidity[i], 1)})
        messageResponseRaw['sensorSamples'] = sensorSamples

    # Handle bad request
    else:
      syslog.syslog('Received an unexpected request from HTML client.')
      messageResponseRaw['error'] = 'invalidRequest'
      messageResponseRaw['numSensorSamples'] = 0

    # Format & send response
    messageResponseJSON = json.dumps(messageResponseRaw)
    self.write_message(messageResponseJSON)

  def on_close(self):
    syslog.syslog('WebSocket connection closed.')

  def check_origin(self, origin):
    return True


"""
start_webserver() must be called by the main application after the Qt (quamash)
asyncio loop has been instantiated but before it has begun.
"""
def start_webserver():
  application = tornado.web.Application([(r'/ws', WSHandler),])
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(9897)
  tornado.ioloop.IOLoop.current().start()
