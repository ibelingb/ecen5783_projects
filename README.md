# ECEN 5783 - Embedded Interface Design Project 2
Title: ECEN 5783 Embedded Interface Design Project 2
Author: Brian Ibeling and Connor Shapiro
Date: 10/6/2019  

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

## Starting and Stopping the Application
To start the server-side applications, simply type the following from the cloned project repository directory.
  > ./startApp.sh

To launch the web-based client, simply open the following file from a browser on a RPi/PC remotely connected to server RPi.
  > project2_webclient.html
NOTE: Server-side RPi server applications required to be started before launching web-based client.
NOTE: May be required to update IP address of server-side RPi on ~line 160 of project2_webclient.html.

To stop the server-side applications, simply type the following from the cloned project repository directory.
  > ./stopApp.sh

# Project Work
Brian Ibeling
- Project1 contributions
- NodeJS Server Instance with MySQL connection and interface
- NodeJS Server and Webpage client JSON Packet definition and interactions
- HTML Webpage design and layout
- HTML Webpage button layout and interactions
- HTML Webpage Speed Test table population and speed test time calulcations
- HTML Webpage Client-NodeJS server error handling

Connor Shaprio
- 

# Project Additions
- Error handling between HTML client and NodeJS server on server/SQL error events.
- Stop script added to kill server-side applications.
