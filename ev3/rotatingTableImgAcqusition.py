# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:23:15 2015

@author: Zigaso
"""

from piCameraAPI import *
from ev3API import *
import time
import numpy as np


##########################################
# parameters - brick
##########################################

motor_port = Port.A
color_sensor_port = Port.Four

##########################################
# parameters - table
##########################################

reconstruction_steps = 30
steps_for_full_table_angle = 20160

##########################################
# parameters - capture
##########################################

camera_address = '192.168.32.15'
#folder_pth = "C:/Users/PTIT/Desktop/PTIT/data/acquisitions/test"
folder_pth = "Z:/Work/Research/Development/poletni-tabor/data/acquisitions/zilje30"
file_name = "zilje30"

##########################################
# calibrate the lego table position
##########################################
b = IBrick()

b.set_mode(motor_port, MotorMode.Degrees)
b.set_mode(color_sensor_port, ColorMode.Color)

if b.read_port( color_sensor_port).sivalue != ColorSensorColor.Green:
    b.turn_motor_at_power_with_check(motor_port,power = 100)

while 1:
    
    color = b.read_port( color_sensor_port).sivalue
    time.sleep(0.001)
    
    if color == ColorSensorColor.Green:
    
        b.stop_motor_with_check(motor_port)
        break

b.turn_motor_at_power_with_check(motor_port,power = -100)
time.sleep(0.5)
b.stop_motor_with_check(motor_port)
b.turn_motor_at_power_with_check(motor_port,power = 25)

while 1:
    
    color = b.read_port( color_sensor_port).sivalue
    time.sleep(0.001)
    
    if color == ColorSensorColor.Green:
    
        b.stop_motor_with_check(motor_port)
        break

##########################################
# connect camera to raspberry pi server
##########################################

#camera = IPiCamera(address='192.168.16.219')
#camera = IPiCamera(address='192.168.16.194')

camera = IPiCamera(address=camera_address)
#camera = IPiCamera(address='localhost')

##########################################
# calibrate camera values
##########################################

calibratedValues = camera.calibrate_camera_values(ISO = 200, rotation = 270)

shutter_speed = calibratedValues["shutter_speed"]
awb_gains = calibratedValues["awb_gains"]

##########################################
# rotate table and capture images - 2017 code
##########################################

steps = int(steps_for_full_table_angle / reconstruction_steps)

motor_steps_start = b.read_port(motor_port).sivalue
time.sleep(0.5)
motor_steps_made = 0

itern = 0
for itern in range(reconstruction_steps+1):
    if itern > 0:
        print('Moving to angle: {0}'.format((itern)/reconstruction_steps*360))
        motor_steps_end = b.read_port(motor_port).sivalue
        b.step_motor_at_power_wait_for_completion(motor_port, power=50, steps = steps, brake=True)    
        time.sleep(1)
        while abs(b.read_port(motor_port).sivalue - motor_steps_end) > 0:
            motor_steps_end = b.read_port(motor_port).sivalue
            time.sleep(1)
        
        motor_steps_made = abs(motor_steps_end - motor_steps_start)
    
    current_angle = (motor_steps_made % steps_for_full_table_angle)/steps_for_full_table_angle*360.0
        
    print('Reached angle: {0}'.format(current_angle))
    
    image_name = file_name + '_' + "{0:.2f}".format(current_angle)
    
    image = camera.capture_image(folder_name = folder_pth, image_name = image_name,shutter_speed = shutter_speed, awb_gains = awb_gains, rotation=270)

b.stop_motor_with_check(motor_port)


###########################################
## rotate table and capture images - 2015 code
###########################################
#
#
#min_steps = 100
#
#steps = np.arange(0,steps_for_full_table_angle+1,steps_for_full_table_angle/reconstruction_steps).round()
#steps = steps[1:]
#
#motor_steps_start = b.read_port(motor_port).sivalue
#motor_steps_made = 0
#
#for step in range(reconstruction_steps+1):
#        
#    if step > 0:
#        step_to_search = (motor_steps_made + min_steps)
#        
#        step_to_search = step_to_search%steps_for_full_table_angle
#        
#        min_steps_diff = steps-step_to_search        
#        min_steps_diff = min_steps_diff[(min_steps_diff>0)]
#        
#        next_step = min_steps_diff[min_steps_diff.argmin()] + step_to_search
#        steps_to_run = min_steps_diff[min_steps_diff.argmin()] + min_steps
#        
#        steps = np.delete(steps,np.where(steps == next_step)[0])
#        
#        b.step_motor_at_power_wait_for_completion(motor_port, power=10, steps = int(steps_to_run), brake=True)
#        time.sleep(1)    
#    
#    motor_steps_end = b.read_port(motor_port).sivalue
#    
#    motor_steps_made = abs(motor_steps_end - motor_steps_start)
#    
#    current_angle = (motor_steps_made % steps_for_full_table_angle)/steps_for_full_table_angle*360
#    
#    if motor_steps_made%steps_for_full_table_angle == 0 & step > 0:
#        current_angle = 360
#    
#    image_name = file_name + '_' + "{0:.2f}".format(current_angle)
#    
#    #image = camera.capture_image(folder_name = folder_pth, image_name = image_name,shutter_speed = shutter_speed, awb_gains = awb_gains)
#    image = camera.capture_image(folder_name = folder_pth, image_name = image_name,shutter_speed = 1000000, awb_gains = awb_gains)
#
#
#b.stop_motor(motor_port)

###########################################
## rotate table and capture images -> old routine
###########################################
#
#reconstruction_steps = 60
#folder_pth = "tree"
#image_name_default = folder_pth
#
#for step in range(reconstruction_steps+1):
#    
#    current_angle = 360 * step / reconstruction_steps
#    image_name = image_name_default + '_' + str(step) + '_' + str(int(current_angle))
#    
#    if step > 0:
#        b.step_motor_at_power(Port.D, power=8, steps = int(2520/reconstruction_steps), brake=True)
#        time.sleep(2)
#        
#    #image = camera.capture_image(folder_name = folder_pth, image_name = image_name,shutter_speed = shutter_speed, awb_gains = awb_gains)
#    image = camera.capture_image(folder_name = folder_pth, image_name = image_name,shutter_speed = 1000000, awb_gains = awb_gains)