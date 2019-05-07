# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:17:49 2015

@author: Zigaso
@author: TimJ

run on Raspberry Pi 
starts listening for image capturing requests
"""

from piCameraServerAPI import *

cameraServer = IPiCameraServer('0.0.0.0')
cameraServer.start_server()
