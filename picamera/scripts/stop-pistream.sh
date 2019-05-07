#!/bin/bash
ps axu | grep "/home/pi/poletni-tabor/picamera/runPiCameraStream.py" | grep -v grep | awk '{print $2}' | sudo xargs kill
