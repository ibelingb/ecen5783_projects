#!/usr/bin/python3

""" db.py: Interface for MySQL Database instance to hold timestamped sensor data

    TODO

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
        - https://pythonspot.com/mysql-with-python/
        - https://softwareengineering.stackexchange.com/questions/261933/using-one-database-connection-across-multiple-functions-in-python
        - http://g2pc1.bu.edu/~qzpeng/manual/MySQL%20Commands.htm        
        
"""

import sys
import MySQLdb

def initializeDatabase():
    db = MySQLdb.connect(host="localhost",
                        user="piuser",
                        passwd="password",
                        db="project1")
    
    # Create a Cursor object to execute queries
    cur = db.cursor()
    
    # Create DB instance for project1 if one doesn't exist
    cur.execute("CREATE DATABASE IF NOT EXISTS project1")
    cur.execute("USE project1")    
    
    # Create table to store DTH22 Temp and humidity sensor data by timestamp
    cur.execute("CREATE TABLE IF NOT EXISTS sensors \
               (timestamp TIMESTAMP, temp FLOAT(3,1), humidity FLOAT(3,1), PRIMARY KEY (timestamp))")
    
    # Select data from table via SQL query
    cur.execute("SELECT * FROM sensors")
    
    # TODO - add check if dataset returned is empty - ignore. 
    if(cur.rowcount != 0) :    
        # Print data currently in table
        for row in cur.fetchall() :
            print (row[0], " ", row[1], " ", row[2])

    db.commit()
    
    return 0

def insertSensorData(temp: float, humidity: float):
    db = MySQLdb.connect(host="localhost",
                        user="piuser",
                        passwd="password",
                        db="project1")
    
    # Create a Cursor object to execute queries
    cur = db.cursor()
    
    # Write received sensor values to database
    cur.execute("INSERT INTO sensors(timestamp, temp, humidity) VALUES (NULL, %s, %s)" % (temp, humidity))
    
    db.commit()
    
    return 0
