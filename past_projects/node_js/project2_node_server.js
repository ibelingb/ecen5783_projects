/*
File: project2_node_server.js
Author: Brian Ibeling
Date: 10/2/2019
Description: NodeJS WebSocket server instance to provide an interface between the Project1 MySQL
             database and the Project2 HTML webpage. Server begins by connecting to the project1
             database 

  + Resources and Citations +
  The following resources were used to assist with development of this SW.
    - https://www.w3schools.com/nodejs/nodejs_mysql_select.asp
    - https://www.pubnub.com/blog/nodejs-websocket-programming-examples/
    - https://stackoverflow.com/questions/31875621/how-to-properly-return-a-result-from-mysql-with-node
    - https://stackoverflow.com/questions/11151632/passing-an-object-to-client-in-node-express-ejs/18106721
    - https://stackoverflow.com/questions/34385499/how-to-create-json-object-node-js
*/

//-----------------------------------------------------------------------------------
var mysql = require('mysql');

// Establish connection to project1 MySQL DB and provide variable to be used for NodeJS SQL queries.
var mysqlCon = mysql.createConnection({
  host: "localhost",
  user: "piuser",
  password: "BestPasswordEver",
  database: "project1"
});
mysqlCon.connect(function(err) {
  if (err) {
    console.log("ERROR: NodeJS Server failed to connect to MySQL DB.");
    return;
  }
  console.log("MySQL DB connected");
});

//-----------------------------------------------------------------------------------
// Query and return sensor data from Project1 SQL sensors DB table based on numSamples parameter provided.
// @numSamples - Number of SQL sensors table entries to retrieve and return
// @return - JSON object with array of SQL sensors table data entries and num table entries returned.
function getSensorData(numSamples, callback) {
  var query = ("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT " + numSamples);
  
  mysqlCon.query(query, function (err, result, fields) {
    // If error occurs, return resulting JSON object with num entries return set to 0 for client error handling.
    if (err) {
      console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB");
      return callback(result, 0);
    }
    return callback(result, result.length);
  });
}

//-----------------------------------------------------------------------------------
// Variables for NodeJS WebSocket-Client interaction
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

// The following handles interactions between the WS server and WebSocket clients
wsServer.on('request', function(request) {
    // Establish new client connection - log event to terminal
    const connection = request.accept(null, request.origin);
    console.log("NodeJS Client has connected.");

    // Data request received from HTML client
    // Read request type and return corresponding data in JSON formatted string
    // Each JSON formatting string returned to client contains:
    //  - The type of request being handled (cmdResponse)
    //  - the number of SQL data entries retrieved and being returned (numSensorSamples)
    //  - An array of the SQL entries requested (sensorSamples)
    connection.on('message', function(message) {

      // Clear dataPacket from last request
      dataPacket.numSensorSamples = '0';
      dataPacket[key] = [];

      // Client request for latest data entry in SQL DB.
      if(message.utf8Data == "getLatestDbData") 
      {
        dataPacket.cmdResponse = "getLatestDbData";
        getSensorData(1, function(sensorSamples, numSamplesReturned){
          dataPacket.numSensorSamples = numSamplesReturned;
          if(numSamplesReturned > 0)
            dataPacket[key].push(sensorSamples[0]);
          connection.send(JSON.stringify(dataPacket));
        });
      }
      // Client request for last 10 data entries in SQL DB.
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

    // On client disconnect event - log event to terminal
    connection.on('close', function(reasonCode, description) {
        console.log('NodeJS Client has disconnected.');
    });
});

//-----------------------------------------------------------------------------------
