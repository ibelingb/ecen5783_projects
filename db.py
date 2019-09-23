#!/usr/bin/python3

""" db.py: Interface for MySQL Database instance to hold timestamped sensor data

    db.py provides an interface for the MySQL database storing timestamped DTH22 sensor data.
    Initialization and connection to the MySQL DB is specified by the credential provided at
    the top of this file.

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://pythonspot.com/mysql-with-python/
        - https://softwareengineering.stackexchange.com/questions/261933/using-one-database-connection-across-multiple-functions-in-python
        - http://g2pc1.bu.edu/~qzpeng/manual/MySQL%20Commands.htm
        - https://stackoverflow.com/questions/28365580/typeerror-int-object-is-not-iterable-python
"""

import sys
import MySQLdb

__author__ = "Brian Ibeling"

HOSTNAME="localhost"
USERNAME="piuser"
PASSWORD="BestPasswordEver"
DATABASE="project1"

#-----------------------------------------------------------------------
def getDbConnection():
    """ Connect to MySQL DB with default credentials """
    db = MySQLdb.connect(host=HOSTNAME,
                        user=USERNAME,
                        passwd=PASSWORD,
                        db=DATABASE)
    return db
#-----------------------------------------------------------------------
def initializeDatabase():
    """ Establish connection to project1 DB, creating one if it does not exist. 
        Also creates the sensors table, which includes a timestamp column as the primary key, with
        temperature and humidity stored as floating point values as the additional columns.
    """
    db = getDbConnection()
    
    # Create a Cursor object to execute queries
    cur = db.cursor()
    
    # Create DB instance for project1 if one doesn't exist
    cur.execute("CREATE DATABASE IF NOT EXISTS project1")
    cur.execute("USE project1")    
    
    # Create table to store DTH22 Temp and humidity sensor data by timestamp
    cur.execute("CREATE TABLE IF NOT EXISTS sensors \
               (timestamp TIMESTAMP, temp FLOAT(3,1), humidity FLOAT(3,1), PRIMARY KEY (timestamp))")

    db.commit()
    
    return 0
#-----------------------------------------------------------------------
def insertSensorData(temp: float, humidity: float):
    """ Insertion of temperature and humidity data to the sensors table within the project1 DB.
        - @temp (float)     : Temperature value to write to DB, stored as degrees celcius.
        - @humidity (float) : Humidity value to write to DB, stored as a percentage.
    """
    db = getDbConnection()
    
    # Create a Cursor object to execute queries
    cur = db.cursor()
    
    # Write received sensor values to database
    cur.execute("INSERT INTO sensors(timestamp, temp, humidity) VALUES (NULL, %s, %s)" % (temp, humidity))
    
    db.commit()
    
    return 0
#-----------------------------------------------------------------------
def getRecentTempData(numSamples: int):
    """ Method to retrieve the last [numSamples] temperature values from the sensors table 
        of the Project1 DB as an array of values.
        If the requested number of samples is greater than the number of samples available,
        only the number of samples available is returned.
        - @numSamples (int) : The number of temperature samples to return.
        - @return: timestampArray[numSamples], tempArray[numSamples]
    """
    timestampArray = [None] * numSamples
    tempArray = [None] * numSamples
    
    db = getDbConnection()
    
    # Create a Cursor object to execute queries
    cur = db.cursor()
    
    # Select data from table via SQL query
    cur.execute("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT %s", (numSamples,))
    
    # If the number of samples captured is less than numSamples, update array size accordingly
    if(cur.rowcount < numSamples):
        timestampArray = [None] * cur.rowcount
        tempArray = [None] * cur.rowcount
    
    # Populate received data into respective arrays
    i = 0
    if(cur.rowcount != 0) :    
        for row in cur.fetchall() :
            timestampArray[i] = row[0]
            tempArray[i] = row[1]
            i += 1
    
    return timestampArray, tempArray
#-----------------------------------------------------------------------
def getRecentHumidityData(numSamples: int):
    """ Method to retrieve the last [numSamples] humidity values from the sensors table 
        of the Project1 DB as an array of values.
        If the requested number of samples is greater than the number of samples available,
        only the number of samples available is returned.
        - @numSamples (int) : The number of humidity samples to return.
        - @return: timestampArray[numSamples], humidityArray[numSamples]
    """
    timestampArray = [None] * numSamples
    humidityArray = [None] * numSamples
    
    db = getDbConnection()
    
    # Create a Cursor object to execute queries
    cur = db.cursor()
    
    # Select data from table via SQL query
    cur.execute("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT %s", (numSamples,))
    
    # If the number of samples captured is less than numSamples, update array size accordingly
    if(cur.rowcount < numSamples):
        timestampArray = [None] * cur.rowcount
        humidityArray = [None] * cur.rowcount
    
    # Populate received data into respective arrays
    i = 0
    if(cur.rowcount != 0) :    
        for row in cur.fetchall() :
            timestampArray[i] = row[0]
            humidityArray[i] = row[2]
            i += 1
    
    return timestampArray, humidityArray
#-----------------------------------------------------------------------
