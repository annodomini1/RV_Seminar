# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:23:15 2015

@author: Zigaso
@author: TimJ


"""
from PIL import Image
import os
from piCameraAPI import *

camera = IPiCamera(address='192.168.32.15')

#%%

calibratedValues = camera.calibrate_camera_values()

shutter_speed = calibratedValues["shutter_speed"]
awb_gains = calibratedValues["awb_gains"]

#%%

#return_msg = camera.capture_image()
#folder_pth = "C:/Users/PTIT/Desktop/PTIT/data/acquisitions/test"
folder_pth = "Z:/Work/Research/Development/poletni-tabor/acquisitions"
image_name = 'caliber.jpg'
camera.capture_image(image_name = image_name, folder_name=folder_pth, shutter_speed = shutter_speed, awb_gains = awb_gains, rotation=270)
# camera.capture_image(image_name = image_name, shutter_speed = 20000, awb_gains = (1.03, 1.13), rotation=270, saturation=-100, brightness=60, contrast=50,resolution = (972,1296))

im = Image.open(os.path.join('test',image_name))
im.show()
