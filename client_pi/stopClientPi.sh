#!/bin/bash
# ECEN 5783 - Embedded Interface Design
# 12/7/2019
# Author: Brian Ibeling
# Description: Script to kill launched SuperProject client_pi processes.

# Kill launched python GUI application and AWS Data Pusher
echo "Killing SuperProject client_pi..."
kill -15 `pidof python3` &
