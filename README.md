# ECEN 5783 - Embedded Interface Design Project 1
Title: ECEN 5783 Embedded Interface Design Project 1
Author: Brian Ibeling
Date: 9/23/2019

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

## Starting the Application
To run the application, simply type the following from the clone project repository directory.
> python3 project1.py


# Project Work
All code developed for this project was done by myself. My partner (Connor Shapiro) will be available for Project 2 onward.

# Project Additions
- Added error text highlighting for when the sensor failed to be read properly or if the returned sensors values exceeded the specified limits. Additionally, highlights green if sensors values are within nominal limits.
- Status to indicate when the sensor sampling timer was complete (after 30 collected samples).
- Added the creation of the project1 DB table to be generated dynamically if one doesn't exist.
- If less than 10 entries in DB table, graphs will only display the data available.
