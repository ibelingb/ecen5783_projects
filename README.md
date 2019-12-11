# ECEN 5783 - Embedded Interface Design Superproject
Title: ECEN 5783 Embedded Interface Design Superproject
Author: Brian Ibeling and Connor Shapiro  
Date: 12/11/2019  

# Install and Execution Instructions
## Client Pi
### Required Python Libraries
Before running the client-pi and AWS applications, the following packages must be installed on the Rpi in use via pip3:
  > sudo pip install AWSIoTPythonSDK  
  > sudo pip install pyzmq  
  > sudo pip install boto3

### Starting and Stopping the Application
To start the client-pi application , simply type the following from the cloned project repository directory.
  > ./startClientPi.sh

To stop the client-pi application, simply type the following from the cloned project repository directory.
  > ./stopClientPi.sh


## Server Pi
### Database Install and User Creation
Prior to running the downloaded application, it is required that a MySQL server instance is available, the 'superproject' database is created, and the user 'piuser' is created and can access the database. Please follow the steps below:

1. NOTE: For development of this project, the MariaDB MySQL server was used.
2. Open MySQL by executing the following command and entering needed credentials:
  > sudo /usr/bin/mysql -u root -p
3. Create the 'piuser' user by exeucting the following commands from MySQL:
  > mariaDB> CREATE USER 'piuser'@'localhost' IDENTIFIED BY 'BestPasswordEver';

  > mariaDB> GRANT ALL PRIVILEGES ON * . * TO 'piuser'@'localhost';

  > mariaDB> FLUSH PRIVILEGES;
4. Create the 'project1' database by executing the following command from MySQL:
  > mariaDB> CREATE DATABASE project1;

### Required Node.js Packages
Before running the server-pi and AWS applications, the following packages must be installed on the Rpi in use via npm:
  > sudo npm install aws-api-gateway-client  
  > sudo npm install express  
  > sudo npm install http  
  > sudo npm install mysql  
  > sudo npm install websocket

### Application Startup
The server-pi application starts automatically, so long as the wand_node_startup systemd service is installed:
  > sudo cp ./wand_node_startup.service /etc/systemd/system/  
  > sudo systemctl enable wand_node_startup