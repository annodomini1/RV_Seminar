# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:23:15 2015

@author: Zigaso
"""

from piCameraAPI import *

camera = IPiCamera(address='192.168.32.15')

calibratedValues = camera.calibrate_camera_values(ISO = 200, rotation = 270)

shutter_speed = calibratedValues["shutter_speed"]
awb_gains = calibratedValues["awb_gains"]

image = camera.capture_image()
#image2 = camera.capture_image(image_name = 'test2',shutter_speed = shutter_speed, awb_gains = awb_gains)

#camera.fetch_image_thread("test","test")
