# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 08:44:05 2015

@author: Zigaso
"""

from piCameraAPI import *

camera = IPiCamera(address = "192.168.32.15")

calibratedValues = camera.calibrate_camera_values(ISO = 200, rotation = 270)

awb_gains = (Fraction(253,254),Fraction(253,254))

# TODO: dodaj smiselne primere za prikaz vplivov nastavitev
camera.capture_image(image_name, folder_name, \
                    shutter_speed, awb_gains, \
                    ISO, rotation, resolution, zoom)

