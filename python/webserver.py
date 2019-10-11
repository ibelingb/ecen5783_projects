#!/usr/bin/python3
#
# ECEN5783
# Author: Connor Shapiro
# 10/7/2019

""" webserver.py: Tornado Webserver python application for EID Project2 to serve DHT22 readings on-demand via WebSockets

  This python application launches a Tornado webserver which waits for a WebSocket connection from a remote device.
  Once connected, the webserver waits for either an on-demand DHT22 sensor reading request,
  or an on-demand data request for the remote client to run a speed test.

  + Resources and Citations +
  The following resources were used to assist with development of this SW.
    - https://web.archive.org/web/20161020184649/http://www.iot-projects.com/index.php?id=websocket-a-simple-example
    - https://www.tornadoweb.org/en/stable/index.html
"""

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from sensor import *
import syslog

__author__ = "Connor Shapiro"

class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        syslog.syslog('WebSocket connection opened.\n')

    def on_message(self, message):
        syslog.syslog('Message received via WebSocket connection.\n')
        if ("reqCurrentReading" == message):
            syslog.syslog('Message received via WebSocket connection.\n')
            hum, temp = sampleDth22()
            messageResponse = "Current humidity is " + str(hum) + ". Current temperature is " + str(temp) + '\n'
        self.write_message(messageResponse)

    def on_close(self):
        syslog.syslog('WebSocket connection closed.\n')

    def check_origin(self, origin):
        return True


application = tornado.web.Application([(r'/ws', WSHandler),])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9897)
    tornado.ioloop.IOLoop.instance().start()
