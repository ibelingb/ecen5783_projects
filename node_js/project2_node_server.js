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
  console.log("Connected!");
  var query = "SELECT * FROM sensors"
  //var query = "SELECT * FROM sensors ORDER BY timestamp DESC LIMIT 10"
  mysqlCon.query(query, function (err, result, fields) {
    if (err) throw err;
    //console.log(result);
  });
});

function getLatestSensorData(numSamples, callback) {
  var query = ("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT " + numSamples);
  
  mysqlCon.query(query, function (err, result, fields) {
    if (err) throw err;
    return callback(result[0]);
  });
}


//-------------------------------------------------
// Node.js WebSocket server 
const http = require('http');
const WebSocketServer = require('websocket').server;

const server = http.createServer();
server.listen(9898);

const wsServer = new WebSocketServer({
    httpServer: server
});

wsServer.on('request', function(request) {
    const connection = request.accept(null, request.origin);

    connection.on('message', function(message) {
      console.log('Received Message:', message.utf8Data);

      getLatestSensorData(3, function(result){
        console.log(result);
        connection.send(result);
      });

      //console.log(data);
      //connection.send(data);
    });
    connection.on('close', function(reasonCode, description) {
        console.log('Client has disconnected.');
    });
});

//-------------------------------------------------

