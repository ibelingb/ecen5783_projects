#!/usr/bin/env python

""" db.py: Interface for MySQL Database instance to hold timestamped sensor data

	TODO

	+ Resources and Citations +
	I used the following example code to assist with development of this SW.
        - https://pythonspot.com/mysql-with-python/
		
"""

import sys
import MySQLdb

# Variables
#cur


def initializeMySql():
    #global cur
    
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
	cur.execute("CREATE TABLE IF NOT EXISTS sensors (id INT(11) NOT NULL AUTO_INCREMENT, timestamp TIMESTAMP, temp FLOAT(3,1), humidity FLOAT(3,1), PRIMARY KEY (id))")
	
	# Select data from table via SQL query
	cur.execute("SELECT * FROM sensors")
	
    # TODO - add check if dataset returned is empty - ignore. 
    # if(cur.rowcount != 0) :
    
    # Print data currently in table
	for row in cur.fetchall() :
		print (row[0], " ", row[1], " ", row[2], " ", row[3])

	return 0

#def addEntryMySql():
#    return 0
