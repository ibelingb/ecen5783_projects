/*
File: wand_node_server.js
Author: Connor Shapiro & Brian Ibeling
Date: 11/16/2019
Description: NodeJS WebSocket server instance to provide an interface between
             the Magic Wand MySQL database and the Magic Wand server HTML
             webpage.

  + Resources and Citations +
  The following resources were used to assist with development of this SW.
    - https://www.w3schools.com/nodejs/nodejs_mysql_select.asp
    - https://www.pubnub.com/blog/nodejs-websocket-programming-examples/
    - https://stackoverflow.com/questions/31875621/how-to-properly-return-a-result-from-mysql-with-node
    - https://stackoverflow.com/questions/11151632/passing-an-object-to-client-in-node-express-ejs/18106721
    - https://stackoverflow.com/questions/34385499/how-to-create-json-object-node-js
    - https://expressjs.com/en/starter/static-files.html
    - https://dzone.com/articles/creating-aws-service-proxy-for-amazon-sqs
    - https://www.npmjs.com/package/aws-api-gateway-client
    - https://stackoverflow.com/questions/13304471/javascript-get-code-to-run-every-minute
*/

//-----------------------------------------------------------------------------
// @@@@@@@@  FUNCTION DECLARATIONS
//
//-----------------------------------------------------------------------------
// Query image filenames from Magic Wand SQL image filename DB table based on numImages
// @numImages - Number of image filename table entries to retrieve and return
// @index - start (in timestamp order) index of image grabs
// @return - JSON object with array of SQL sensors table data entries and num table entries returned.
function getImages(numImages, index, callback) {
  var query = ("SELECT * FROM images ORDER BY timestamp LIMIT " + index + ", " + numImages)
  
  mysqlCon.query(query, function (err, result, fields) {
      // If error occurs, return resulting JSON object with num entries return set to 0 for client error handling.
      if (err) {
        console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
        return callback(result, 0)
      }
      else {
        return callback(result, result.length)
      }
    }
  )
}

//-----------------------------------------------------------------------------
// Query image classification metrics from MySQL
// @correctness - Classification correctness factor
// @return - number of records matching correctness
async function getImageMetrics(correctness, callback) {
  var query = ("SELECT * FROM images WHERE correctness=" + correctness)
  mysqlCon.query(query, function (err, result, fields) {
      // If error occurs, return resulting JSON object with num entries return set to 0 for client error handling.
      if (err) {
        console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
        return callback(result, 0)
      }
      else {
        return callback(result.length)
      }
    }
  )
}

//-----------------------------------------------------------------------------
// Query voice recognition metrics from MySQL
// @return - number of records matching correctness
async function getAudioMetrics(callback) {
  var query = ("SELECT * FROM recognizedCmds")
  mysqlCon.query(query, function (err, result, fields) {
      // If error occurs, return resulting JSON object with num entries return set to 0 for client error handling.
      if (err) {
        console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
        return callback(result, 0)
      }
      else {
        return callback(result)
      }
    }
  )
}

//-----------------------------------------------------------------------------
// Async helper function to get metrics gathered with a promise.
async function gatherMetrics() {
  metricsPacket.cmdResponse = 'getMetrics'
  await getImageMetrics(0, function(quantity) {
      metricsPacket.numCorrect = quantity
    }
  )
  await getImageMetrics(1, function(quantity) {
      metricsPacket.numIncorrect = quantity
    }
  )
  await getImageMetrics(2, function(quantity) {
      metricsPacket.numUnknown = quantity
    }
  )
  await getAudioMetrics(function(data) {
      metricsPacket.numRecognized = 0
      metricsPacket.numUnrecognized = 0
      for (i = 0; i < data.length; i++)
      {
        if (1 == data[i].cmdRecognized)
          metricsPacket.numRecognized++
        else if (0 == data[i].cmdRecognized)
          metricsPacket.numUnrecognized++
      }
    }
  )
}

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
      console.log('Successfully deleted SQS record.')
      // console.log(result.data.DeleteMessageResponse)
    }).catch(function(result){
      console.log('ERROR deleting SQS record.')
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
      if (null == result.data.ReceiveMessageResponse.ReceiveMessageResult.messages)
      {
        // console.log('SQS is apparently empty.')
      }
      else {
        var receivedRecord = result.data.ReceiveMessageResponse.ReceiveMessageResult.messages[0]
        var parsedRecord

        // Deal with possibility of new Lambda records and old records
        if (JSON.parse(receivedRecord.Body).hasOwnProperty('version')) {
          parsedRecord = JSON.parse(receivedRecord.Body).requestPayload
          // console.log(parsedRecord)
          var then = new Date(JSON.parse(receivedRecord.Body).timestamp)
          recordTimestamp = Math.round(then.getTime() / 1000)
          // console.log(recordTimestamp)
        }
        else {
          parsedRecord = JSON.parse(receivedRecord.Body)
          // console.log(parsedRecord)
          // since these early-dev records have no creation timestamp, use the current time
          const now = new Date()
          recordTimestamp = Math.round(now.getTime() / 1000)
          // console.log(recordTimestamp)
        }

        var query = ''
        var boolToInt
        var correctnessInt
        switch (parsedRecord.recordType) {
          case 'imageLink':
            // imageLink records are vestigial (thanks to imageLabel) so delete them
            deleteOneRecord(receivedRecord.ReceiptHandle)
          break

          case 'imageLabel':
            /* Get timestamp from image filename, rather than AWS metadata */
            const year = parsedRecord.image.substr(8,4)
            const month = parsedRecord.image.substr(4,2) - 1
            const day = parsedRecord.image.substr(6,2)
            const hour = parsedRecord.image.substr(13,2)
            const minute = parsedRecord.image.substr(15,2)
            const second = parsedRecord.image.substr(17,2)
            then = new Date(year, month, day, hour, minute, second)
            recordTimestamp = Math.round(then.getTime() / 1000)

            query = 'INSERT INTO images (filename, timestamp, label, downloaded) VALUES (\'' + parsedRecord.image + '\', ' + recordTimestamp + ', \'' + parsedRecord.label + '\', 0) ON DUPLICATE KEY UPDATE timestamp =' + recordTimestamp + ', label=\'' + parsedRecord.label + '\''
            mysqlCon.query(query, function (err, result, fields) {
                if (err) {
                  console.log("ERROR: NodeJS server failed to insert data into MySQL DB")
                  console.log(err)
                }
                else {
                  deleteOneRecord(receivedRecord.ReceiptHandle)
                }
              }
            )
          break

          case 'cmdRecognized':
            if (parsedRecord.cmdRecognized == 'True') {
              boolToInt = '1'
            }
            else {
              boolToInt = '0'
            }
            query = 'INSERT INTO recognizedCmds VALUES(' + recordTimestamp + ', ' + boolToInt + ')'
            mysqlCon.query(query, function (err, result, fields) {
                if (err) {
                  console.log("ERROR: NodeJS server failed to insert data into MySQL DB")
                  console.log(err)
                }
                else {
                  deleteOneRecord(receivedRecord.ReceiptHandle)
                }
              }
            )

          break

          case 'imageTag':
              switch (parsedRecord.tag) {
                case 'correct':
                  correctnessInt = 0
                break

                case 'incorrect':
                  correctnessInt = 1
                break

                default:
                  correctnessInt = 2
                break
              }
              
              query = 'INSERT INTO images (filename, correctness, downloaded) VALUES (\'' + parsedRecord.image + '\', \'' + correctnessInt + '\', 0) ON DUPLICATE KEY UPDATE correctness=\'' + correctnessInt + '\''
              mysqlCon.query(query, function (err, result, fields) {
                  if (err) {
                    console.log("ERROR: NodeJS server failed to insert data into MySQL DB")
                    console.log(err)
                  }
                  else {
                    deleteOneRecord(receivedRecord.ReceiptHandle)
                  }
                }
              )
          break

          default:
            // clear out test messages
            if (parsedRecord.message == 'Hello from AWS IoT console') {
              console.log("Removing test record")
              deleteOneRecord(receivedRecord.ReceiptHandle)
            }
            else {
              console.log("ERROR: Unknown recordType received from SQS.")
            }
          break
        }
      }
    }).catch(function(result){
      console.log('ERROR getting record from SQS.')
      console.log(result)
    })
}

//-----------------------------------------------------------------------------------
// Grab an image from S3 via the AWS API Gateway
function getOneImage(imageFilename) {
  const fs = require('fs')

  /* API Gateway params */
  var pathParams = {
    item: 'b64_' + imageFilename
  }
  var resource = '/v1/image/b64_' + imageFilename
  var method = 'GET'
  var additionalParams = {
    headers: '',
    queryParams: ''
  }
  var body = ''

  apigClient.invokeApi(pathParams, resource, method, additionalParams, body)
    .then(function(result) {
      // console.log(result.data)
      let buf = new Buffer.from(result.data, 'base64')
      fs.writeFileSync('/home/pi/superproject_images/' + imageFilename, buf)
      const query = 'UPDATE images SET downloaded=1 WHERE filename=\'' + imageFilename + '\''
      mysqlCon.query(query, function (err, result, fields) {
          if (err) {
            console.log("ERROR: NodeJS server failed to update data in MySQL DB")
            console.log(err)
          }
          else {
            // console.log("Success: " + result)
          }
        }
      )
    }).catch(function(result){
      console.log('ERROR getting ' + imageFilename + ' from API Gateway.')
      console.log(result)
    })
}

//-----------------------------------------------------------------------------------
// Check if any images need to be grabbed from S3, if so grab them
function getNeededImage() {

  const query = 'SELECT filename FROM images WHERE downloaded=0 ORDER BY timestamp DESC LIMIT 1'
  mysqlCon.query(query, function (err, result, fields) {
      if (err) {
        console.log("ERROR: NodeJS server failed to retrieve data from MySQL DB")
        console.log(err)
      }
      else {
        if (result.length) {
          getOneImage(result[0].filename)
        }
        else {
          // Nothing to do!
        }
      }
    }
  )
}


//-----------------------------------------------------------------------------
// @@@@@@@@  MAIN LOOP
//

/* Global (inter-module) Variables *******************************************/
var page = 0  // Used to track which set of 10 images the images page is on
var maxPage = false  // Used to prevent advancing set of 10 images past end

/* MySQL Setup ***************************************************************/
//-----------------------------------------------------------------------------
// Variables for MySQL
var mysql = require('mysql')
var mysqlCon = mysql.createConnection(
  {
    host: "localhost",
    user: "piuser",
    password: "BestPasswordEver",
    database: "superproject"
  }
)


//-----------------------------------------------------------------------------
// Setup calls for MySQL

/* Establish connection to MySQL DB and provide variable to be used for NodeJS
 * SQL queries.
 */
mysqlCon.connect(function(err) {
    if (err) {
      console.log("ERROR: NodeJS Server failed to connect to MySQL DB.")
    }
    else {
      console.log("MySQL DB connected")
    }
  }
)

/* HTTP Image Server Setup ***************************************************/
//-----------------------------------------------------------------------------
// Variables for Node.JS HTTP-accessible image server
var express = require('express')
var imageServer = express()

//-----------------------------------------------------------------------------
// Setup calls for image server
imageServer.use(express.static('/home/pi/superproject_images'))
imageServer.listen(50012)

/* WebSocket Setup ***********************************************************/
//-----------------------------------------------------------------------------
// Variables for NodeJS WebSocket-Client interaction

// Create empty dataPacket object for client response data
var dataPacket = {cmdResponse: "", numImages: "0"}
var key = "images"
dataPacket[key] = []


var metricsPacket = {
  cmdResponse: "",
  numCorrect: "0",
  numIncorrect: "0",
  numUnknown: "0",
  numRecognized: "0",
  numUnrecognized: "0"
}

var i = 0

// Initialize Node.js WebSocket server 
const http = require('http')
const WebSocketServer = require('websocket').server
const server = http.createServer()
const wsServer = new WebSocketServer (
  {
    httpServer: server
  }
)

//-----------------------------------------------------------------------------
// Setup calls for WebSocket

server.listen(9898)

// The following handles interactions between the WS server and WebSocket clients
wsServer.on('request', function(request) {
    // Establish new client connection - log event to terminal
    const connection = request.accept(null, request.origin)
    console.log("HTML client has connected.")

    // Data request received from HTML client
    // Read request type and return corresponding data in JSON formatted string
    // Each JSON formatting string returned to client contains:
    //  - The type of request being handled (cmdResponse)
    //  - the number of SQL data entries retrieved and being returned (numImages)
    //  - An array of the SQL entries requested (images)
    connection.on('message', function(message) {
        // Clear dataPacket from last request
        dataPacket.numImages = '0'
        dataPacket[key] = []

        // Client request for latest data entry in SQL DB.
        if (message.utf8Data == "getLatestImage") 
        {
          dataPacket.cmdResponse = "getLatestImage"
          getImages(1, 0, function(images, numImagesReturned) {
              dataPacket.numImages = numImagesReturned
              if (numImagesReturned > 0)
                dataPacket[key].push(images[0])
              connection.send(JSON.stringify(dataPacket))
            }
          )
        }
        // Client request for 10 images
        else if (message.utf8Data == "get10Images") 
        {
          dataPacket.cmdResponse = "get10Images"
          getImages(10, 10 * page, function(images, numImagesReturned){
              dataPacket.numImages = numImagesReturned
              for(i = 0; i < numImagesReturned; i++) {
                dataPacket[key].push(images[i])
              }
              connection.send(JSON.stringify(dataPacket))
            }
          )
        }
        // Client request to increase image index by 10
        else if (message.utf8Data == "next10Images") 
        {

          /* Guard against access non-existent image index */
          if (!maxPage) {
            page += 1
          }

          dataPacket.cmdResponse = "get10Images"
          getImages(10, 10 * page, function(images, numImagesReturned) {
            
              if (10 > numImagesReturned) {
                maxPage = true
              }

              dataPacket.numImages = numImagesReturned
              for(i = 0; i < numImagesReturned; i++) {
                dataPacket[key].push(images[i])
              }
              connection.send(JSON.stringify(dataPacket))
            }
          )
        }
        // Client request to decrease image index by 10
        else if (message.utf8Data == "prev10Images") 
        {
          /* Prevent accessing negative image index */
          if (page > 0) {
            page -= 1
            maxPage = false
          }

          dataPacket.cmdResponse = "get10Images"
          getImages(10, 10 * page, function(images, numImagesReturned){
              dataPacket.numImages = numImagesReturned
              for(i = 0; i < numImagesReturned; i++) {
                dataPacket[key].push(images[i])
              }
              connection.send(JSON.stringify(dataPacket))
            }
          )
        }
        // Client request for metrics counts
        else if (message.utf8Data == "getMetrics")
        {
          connection.send(JSON.stringify(metricsPacket))
        }
      }
    )

    // On client disconnect event - log event to terminal
    connection.on('close', function(reasonCode, description) {
      
        /* Since moving from main page to image page resets the WebSocket,
         * it's easiest to just reset page to 0 on each connection close.
         */
        page = 0
        maxPage = false 

        console.log('HTML client has disconnected.')
      }
    )
  }
)


/* AWS API Gateway Setup *****************************************************/
//-----------------------------------------------------------------------------
// Variables for AWS API Gateway
var apigClientFactory = require('aws-api-gateway-client').default
var apigCredentials = require('./credentials.js')  // Hardcoded apiKey is not distributed via git
var apigConfig = {
  invokeUrl:'https://l8htk90vrb.execute-api.us-east-1.amazonaws.com/production',
  region: 'us-east-1',
  accessKey: apigCredentials.credKey,
  secretKey: apigCredentials.credSecret,
  sessionToken: apigCredentials.credToken
}
var apigClient = apigClientFactory.newClient(apigConfig)

//-----------------------------------------------------------------------------
// Setup calls for main program

gatherMetrics()  // Build the metrics JSON

/* Attempt to grab new SQS records, undownloaded images, and re-build the
 * metrics JSON at fixed intervals
 */
setInterval(getNeededImage, 7 * 1000)
setInterval(getOneRecord, 4 * 1000)
setInterval(gatherMetrics, 60 * 1000)