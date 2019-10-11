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
from sensor import *
import syslog
import json

__author__ = "Connor Shapiro"

MAX_RETRIES = 3

class WSHandler(tornado.websocket.WebSocketHandler):

  def open(self):
    syslog.syslog('WebSocket connection opened.\n')

  def on_message(self, message):
    syslog.syslog('Message received via WebSocket connection.\n')

    # Expect plaintext request messages from the HTML client
    if ("reqCurrentReading" == message):
      syslog.syslog('Sensor reading requested. Beginning sensor reading.\n')
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
                      ' attempts.\n')
        messageResponse = json.dumps({'error': 1,
                                      'errorType': 'sensorHardware'})
      else:
        syslog.syslog('Sensor reading succeeded.\n')
        messageResponse = json.dumps({'error': 0, 'humidity': humidity,
                                      'temperature': temperature})

    elif ("reqSpeedTest" == message):
      pass
    else:
      messageResponse = json.dumps({'error': 1, 'errorType': 'invalidRequest'})

    self.write_message(messageResponse)

  def on_close(self):
    syslog.syslog('WebSocket connection closed.\n')

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
