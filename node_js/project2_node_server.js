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

function getLatestSensorData(numSamples, callback) {
  var query = ("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT " + numSamples);
  
  mysqlCon.query(query, function (err, result, fields) {
    if (err) throw err;
    return callback(result);
  });
}


//-------------------------------------------------
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
      console.log('Received Message:', message.utf8Data);

      if(message.utf8Data == "getLatestDbData") {        
        getLatestSensorData(1, function(result){
          connection.send(JSON.stringify(result[0]));
        });
      }

    });

    // On client disconnect event
    connection.on('close', function(reasonCode, description) {
        console.log('Client has disconnected.');
    });
});

wsServer.onmessage = function(e) {

}

//-------------------------------------------------

