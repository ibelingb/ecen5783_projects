#!/bin/bash
# ECEN 5783 - Embedded Interface Design
# 10/6/2019
# Authors: Brian Ibeling and Connor Shapiro
# Description: Startup script to launch project1 Python GUI application
#              and project2 NodeJS Server and Tornado Server.

# Start python applciation
python3 python/project1.py &

# Start NodeJS Server applciation
node node_js/project2_node_server.js &

# Start Tornado Server applciation
## TODO
