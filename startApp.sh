#!/bin/bash
# ECEN 5783 - Embedded Interface Design
# 10/6/2019
# Authors: Brian Ibeling and Connor Shapiro
# Description: Startup script to launch project1 Python GUI application
#              and project2 NodeJS Server and Tornado Server.

# Create MySQL DB and sensors table if neither exists
mysql --user="piuser" --password="BestPasswordEver" --execute="CREATE DATABASE IF NOT EXISTS project1; USE project1; \
      CREATE TABLE IF NOT EXISTS sensors (timestamp TIMESTAMP, temp FLOAT(3,1), humidity FLOAT(3,1), PRIMARY KEY (timestamp))"

# Start python applciation
python3 python/project1.py &

# Start NodeJS Server applciation
node node_js/project2_node_server.js &

# Start Tornado Server applciation
## TODO
