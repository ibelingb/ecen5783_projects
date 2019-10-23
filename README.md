# ECEN 5783 - Embedded Interface Design Project 3
Title: ECEN 5783 Embedded Interface Design Project 3
Author: Brian Ibeling and Connor Shapiro  
Date: 10/22/2019  

# Install and Execution Instructions
## Database Install and User Creation
Prior to running the downloaded application, it is required that a MySQL server instance is available, the 'project1' database is created, and the user 'piuser' is created and can access the database. Please follow the steps below:

1. NOTE: For development of this project, the MariaDB MySQL server was used.
2. Open MySQL by executing the following command and entering needed credentials:
  > sudo /usr/bin/mysql -u root -p
3. Create the 'piuser' user by exeucting the following commands from MySQL:
  > mariaDB> CREATE USER 'piuser'@'localhost' IDENTIFIED BY 'BestPasswordEver';

  > mariaDB> GRANT ALL PRIVILEGES ON * . * TO 'piuser'@'localhost';

  > mariaDB> FLUSH PRIVILEGES;
4. Create the 'project1' database by executing the following command from MySQL:
  > mariaDB> CREATE DATABASE project1;

## Required Python Libraries
Before running the server-side and AWS applications, the following packages must be installed on the Rpi in use via pip3:
  > sudo pip install AWSIoTPythonSDK  
  > sudo pip install pyzmq

## Starting and Stopping the Application
To start the server-side applications and connect to AWS, simply type the following from the cloned project repository directory.
  > ./startApp.sh

To launch the web-based client, simply open the following file from a browser on a RPi/PC remotely connected to server RPi.
  > project3_webclient.html
NOTE: Server-side RPi server applications required to be started before launching web-based client.  

To stop the server-side applications, simply type the following from the cloned project repository directory.
  > ./stopApp.sh

# Project Work
Brian Ibeling
- Project1 Python Application modifications and addition of ZMQ.  
- JSON packet definition of Alert and Data records, and passing of data from Python app to AWS.
- Data Pusher Handler python application.  
- AWS IoT and Rules definitions.  
- AWS Lambda connection with AWS IoT to receive Alert.  
- Cost analysis between AWS and Google Cloud.  

Connor Shaprio  
- 

# Project Additions
- Extra credit completed to display the number of records current in the AWS SQS Queue  
- Added use of ZeroMQ to pass data between the Project1 Python GUI and Python Data_Pusher. This allowed the GUI responsiveness to not be interferred with by the AWS connection or data handling.
