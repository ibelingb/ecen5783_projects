#!/bin/bash
# ECEN 5783 - Embedded Interface Design
# 10/6/2019
# Authors: Brian Ibeling and Connor Shapiro
# Description: Script to kill launched project GUI and AWS Data Pusher processes.

# Kill launched python GUI application and AWS Data Pusher
echo "Killing python GUI and AWS IoT Data Pusher..."
kill -15 `pidof python3` &
