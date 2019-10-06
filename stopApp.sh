#!/bin/bash
# ECEN 5783 - Embedded Interface Design
# 10/6/2019
# Authors: Brian Ibeling and Connor Shapiro
# Description: Script to kill launched project1/2 processes.

# Kill launched python GUI applciation
echo "Killing python GUI..."
kill -15 `pidof python3` &

# Kill launched NodeJS Server application
echo "Killing NodeJS Server..."
kill -15 `pidof node` &

# Kill launched Tornado Server application
echo "Killing Tornado Server..."
## TODO
