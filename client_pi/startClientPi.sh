#!/bin/bash
# ECEN 5783 - Embedded Interface Design
# 12/7/2019
# Author: Brian Ibeling
# Description: Startup script to launch SuperProject Python applications
#              for client_pi applications
#
# Sources: 
#   - https://stackoverflow.com/questions/24104123/run-python-script-with-and-without-output
#

# Start client_pi python applications
echo "Launching SuperProject client_pi..."
python3 microphone.py -s > /dev/null 2>&1 &
python3 camera.py &
python3 client_pi.py &

