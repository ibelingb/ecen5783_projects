/*
File: project2_node_server.js
Author: Brian Ibeling
Date: 10/2/2019

TODO: Add description

*/

//-------------------------------------------------
// TODO: Move mysql function to separate NodeJS file
var mysql = require('mysql');

var mysqlCon = mysql.createConnection({
  host: "localhost",
  user: "piuser",
  password: "BestPasswordEver",
  database: "project1"
});

mysqlCon.connect(function(err) {
  if (err) throw err;
  var query = "SELECT * FROM sensors"

  console.log("MySQL DB connected");
  mysqlCon.query(query, function (err, result, fields) {
    if (err) throw err;
  });
});

function getSensorData(numSamples, callback) {
  var query = ("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT " + numSamples);
  
  mysqlCon.query(query, function (err, result, fields) {
    if (err) throw err;
    return callback(result, result.length);
  });
}


//-------------------------------------------------
// Create empty dataPacket object for client response data
var dataPacket = {cmdResponse: "", numSensorSamples: "0"};
var key = "sensorSamples";
dataPacket[key] = [];
var i = 0;

// Initialize Node.js WebSocket server 
const http = require('http');
const WebSocketServer = require('websocket').server;
const server = http.createServer();
server.listen(9898);
const wsServer = new WebSocketServer({
    httpServer: server
});

// The following handles interactions between the WS server and WS clients
wsServer.on('request', function(request) {
    // Establish new client connection
    const connection = request.accept(null, request.origin);
    console.log("Client has connected.");

    // Handle data requests from clients
    connection.on('message', function(message) {

      // Clear dataPacket from last request
      dataPacket.numSensorSamples = '0';
      dataPacket[key] = [];

      if(message.utf8Data == "getLatestDbData") 
      {
        dataPacket.cmdResponse = "getLatestDbData";
        getSensorData(1, function(sensorSamples, numSamplesReturned){
          dataPacket.numSensorSamples = numSamplesReturned;
          dataPacket[key].push(sensorSamples[0]);
          connection.send(JSON.stringify(dataPacket));
        });
      } 
      else if (message.utf8Data == "getLast10Samples") 
      {
        dataPacket.cmdResponse = "getLast10Samples";
        getSensorData(10, function(sensorSamples, numSamplesReturned){
          dataPacket.numSensorSamples = numSamplesReturned;
          for(i=0; i<numSamplesReturned; i++) {
            dataPacket[key].push(sensorSamples[i]);
          }
          connection.send(JSON.stringify(dataPacket));
        });
      }
    });

    // On client disconnect event
    connection.on('close', function(reasonCode, description) {
        console.log('Client has disconnected.');
    });
});

//-------------------------------------------------

