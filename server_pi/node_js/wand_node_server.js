/*
File: wand_node_server.js
Author: Connor Shapiro & Brian Ibeling
Date: 11/16/2019
Description: NodeJS WebSocket server instance to provide an interface between
             the Magic Wand MySQL database and the Magic Wand server HTML
             webpage.

  + Resources and Citations +
  The following resources were used to 
  
  assist with development of this SW.
    - https://www.w3schools.com/nodejs/nodejs_mysql_select.asp
    - https://www.pubnub.com/blog/nodejs-websocket-programming-examples/
    - https://stackoverflow.com/questions/31875621/how-to-properly-return-a-result-from-mysql-with-node
    - https://stackoverflow.com/questions/11151632/passing-an-object-to-client-in-node-express-ejs/18106721
    - https://stackoverflow.com/questions/34385499/how-to-create-json-object-node-js
    - https://expressjs.com/en/4x/api.html
    - https://dzone.com/articles/creating-aws-service-proxy-for-amazon-sqs
    - https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-generate-sdk-javascript.html
    - https://www.npmjs.com/package/aws-api-gateway-client
*/

//-----------------------------------------------------------------------------------
var mysql = require('mysql')

// Establish connection to MySQL DB and provide variable to be used for NodeJS SQL queries.
var mysqlCon = mysql.createConnection({
  host: "localhost",
  user: "piuser",
  password: "BestPasswordEver",
  database: "superproject"
})
mysqlCon.connect(function(err) {
  if (err) {
    console.log("ERROR: NodeJS Server failed to connect to MySQL DB.")
  }
  else {
    console.log("MySQL DB connected")
  }
});

//-----------------------------------------------------------------------------------
// Query image filenames from Magic Wand SQL image filename DB table based on numImages
// @quantity - Number of image filename table entries to retrieve and return
// @return - JSON object with array of SQL sensors table data entries and num table entries returned.
function getImages(numImages, callback) {
  var query = ("SELECT * FROM images ORDER BY uuid DESC LIMIT " + numImages)
  
  mysqlCon.query(query, function (err, result, fields) {
    // If error occurs, return resulting JSON object with num entries return set to 0 for client error handling.
    if (err) {
      console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
      return callback(result, 0)
    }
    else {
      return callback(result, result.length)
    }
  });
}

//-----------------------------------------------------------------------------------
// Variables for NodeJS HTTP-accessible image server
var express = require('express')
var imageServer = express()

imageServer.use(express.static('/home/pi/superproject_images'))
imageServer.listen(50012)


//-----------------------------------------------------------------------------------
// Variables for NodeJS WebSocket-Client interaction
// Create empty dataPacket object for client response data
var dataPacket = {cmdResponse: "", numImages: "0"};
var key = "images";
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
    //  - the number of SQL data entries retrieved and being returned (numImages)
    //  - An array of the SQL entries requested (images)
    connection.on('message', function(message) {

      // Clear dataPacket from last request
      dataPacket.numImages = '0';
      dataPacket[key] = [];

      // Client request for latest data entry in SQL DB.
      if(message.utf8Data == "getLatestImage") 
      {
        dataPacket.cmdResponse = "getLatestImage";
        getImages(1, function(images, numImagesReturned) {
          dataPacket.numImages = numImagesReturned;
          if (numImagesReturned > 0)
            dataPacket[key].push(images[0]);
          connection.send(JSON.stringify(dataPacket));
        });
      }
      // Client request for last 10 data entries in SQL DB.
      else if (message.utf8Data == "getLast10Images") 
      {
        dataPacket.cmdResponse = "getLast10Images";
        getImages(10, function(images, numImagesReturned){
          dataPacket.numImages = numImagesReturned;
          for(i = 0; i < numImagesReturned; i++) {
            dataPacket[key].push(images[i]);
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
// Variables for AWS API Gateway
const fs = require('fs')
var apigClientFactory = require('aws-api-gateway-client').default
var apigCredentials = require('./credentials.js')  // Hardcoded apiKey is not distributed via git
var apigConfig = {
  invokeUrl:'https://l8htk90vrb.execute-api.us-east-1.amazonaws.com/testDecNinth',
  region: 'us-east-1',
  accessKey: 'ASIAYPIUZPZ4OZYEEOP3',
  secretKey: 'rb/0JrCU0tpCPUKryJzZZ5CbgD6v4ZjdIm73VUHN',
  sessionToken: 'FwoGZXIvYXdzEJf//////////wEaDO4lXsB1wW/egMPzdCLKAbkpFM0/TGAuuyoJUbotvPC58oTVT6GdqE7jDt6Z1gd3fWjUYkdHcH7ETQZZXhtYLfenae6tijPFWgAbYcyIn0TaycZg07GUvmv+CTzxZZh2I9yP2Wu+otB38zDbC36GdSbyD/4DCRGKSA7rHPvq5L032G4/ySkrxbQXp71nX3Q3bp92j0GU+RVIe39oGzzJe2swzd9DFLyeDNdJpANapyqUpRDhWqUKaue5Gu4hh+7bF0b+JDZkLZ6EQP7vK8RXrkrcTd5qdVnFYpYoj9a87wUyLTC4k/0lpfFqdC4fzoTYvtmM20eMB0aZEOYEFHbVUEmGVjnDEZHLkjT6nJ0CwQ=='
}
var apigClient = apigClientFactory.newClient(apigConfig)

//-----------------------------------------------------------------------------------
// Delete one record from SQS via API Gateway
function deleteOneRecord(receiptHandle) {
  var pathParams = ''
  var resource = '/v1/delete'
  var method = 'DELETE'
  var additionalParams = {
    headers: '',
    queryParams: {
      ReceiptHandle: receiptHandle
    }
  }
  var body = ''
  
  apigClient.invokeApi(pathParams, resource, method, additionalParams, body)
    .then(function(result) {
      console.log(result.data.DeleteMessageResponse)
    }).catch(function(result){
      console.log('ERROR')
      console.log(result)
    })
}

//-----------------------------------------------------------------------------------
// Pull one record from SQS via API Gateway
function getOneRecord() {
  var recordTimestamp
  var pathParams = ''
  var resource = '/v1/receive'
  var method = 'GET'
  var additionalParams = {
    headers: '',
    queryParams: {
      VisibilityTimeout: '10',
      MaxNumberOfMessages: '1',
      AttributeName: ''
    }
  }
  var body = ''
  
  apigClient.invokeApi(pathParams, resource, method, additionalParams, body)
    .then(function(result) {
      var receivedRecord = result.data.ReceiveMessageResponse.ReceiveMessageResult.messages[0]
      var parsedRecord

      
      // Deal with bug in some old tag and label JSONs
      var regex = '.jpg,'
      var found = receivedRecord.Body.match(regex)
      if (found) {
        receivedRecord.Body = receivedRecord.Body.substr(0, found.index + 4) + "\"" + receivedRecord.Body.substr(found.index + 4, receivedRecord.Body.length)
        console.log(receivedRecord.Body)
        console.log(JSON.parse(receivedRecord.Body))
      }

      // Deal with possibility of new Lambda records and old records
      if (JSON.parse(receivedRecord.Body).hasOwnProperty('version')) {
        parsedRecord = JSON.parse(receivedRecord.Body).requestPayload
        console.log(parsedRecord)
        const then = new Date(JSON.parse(receivedRecord.Body).timestamp)
        recordTimestamp = Math.round(then.getTime() / 1000)
        console.log(recordTimestamp)
      }
      else {
        parsedRecord = JSON.parse(receivedRecord.Body)
        console.log(parsedRecord)
        // since these early-dev records have no creation timestamp, use the current time
        const now = new Date()
        recordTimestamp = Math.round(now.getTime() / 1000)
        console.log(recordTimestamp)
      }

      var query = ''
      var boolToInt
      switch (parsedRecord.recordType) {
        case 'imageLink':
          // imageLink records are vestigial (thanks to imageLabel) so delete them
          deleteOneRecord(receivedRecord.ReceiptHandle)
        break

        case 'imageLabel':
          query = 'INSERT INTO images (filename, label) VALUES (\'' + parsedRecord.image + '\', \'' + parsedRecord.label + '\') ON DUPLICATE KEY UPDATE label=\'' + parsedRecord.label + '\''
          mysqlCon.query(query, function (err, result, fields) {
              if (err) {
                console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
                console.log(err)
              }
              else {
                console.log(result)
                // deleteOneRecord(receivedRecord.ReceiptHandle)
              }
            }
          )
        break

        case 'cmdRecognized':
          if (parsedRecord.cmdRecognized == 'true') {
            boolToInt = '1'
          }
          else {
            boolToInt = '0'
          }
          query = 'INSERT INTO recognizedCmds VALUES(' + recordTimestamp + ', ' + boolToInt + ')'
          mysqlCon.query(query, function (err, result, fields) {
              if (err) {
                console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
                console.log(err)
              }
              else {
                deleteOneRecord(receivedRecord.ReceiptHandle)
              }
            }
          )

        break

        case 'imageTag':

        break

        default:
          // clear out test messages
          console.log(parsedRecord.message)
          if (parsedRecord.message.localCompare('Hello from AWS IoT console')) {
            console.log("Removing test record")
            deleteOneRecord(receivedRecord.ReceiptHandle)
          }
          else {
            console.log("ERROR: Unknown recordType received from SQS.")
          }
        break
      }

    }).catch(function(result){
      console.log('ERROR')
      console.log(result)
    })
}

getOneRecord()

// var pathParams = {
//   //This is where path request params go. 
//   item: 'img_12072019-180625.jpg'
// };
// // Template syntax follows url-template https://www.npmjs.com/package/url-template
// var pathTemplate = '/v1/image/{item}'
// var method = 'GET';
// var additionalParams = {
//   //If there are query parameters or headers that need to be sent with the request you can add them here
//   headers: {
//       param0: '',
//       param1: ''
//   },
//   queryParams: {
//       param0: '',
//       param1: ''
//   }
// };
// var body = {
//   //This is where you define the body of the request
// };

// apigClient.invokeApi(pathParams, pathTemplate, method, additionalParams, body)
//   .then(function(result){
//       //This is where you would put a success callback
//       console.log("SUCCESS")
//       fs.writeFileSync(pathParams.item, result.message)
//   }).catch( function(result){
//     console.log(result.message)
//   });
