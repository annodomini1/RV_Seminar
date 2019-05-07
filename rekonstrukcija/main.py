import sys
sys.path
sys.path.append('C:/Users/lapaj/OneDrive/RVseminar/ev3')
sys.path.append('C:/Users/lapaj/OneDrive/RVseminar/picamera')

from ev3.ev3API import *
import time
from picamera.piCameraAPI import *
import numpy as np

#____________________Init______________________________


camera = IPiCamera(address='192.168.43.78')

calibratedValues = camera.calibrate_camera_values(ISO = 200, rotation = 270)

shutter_speed = calibratedValues["shutter_speed"]
awb_gains = calibratedValues["awb_gains"]

# image = camera.capture_image()
# #image2 = camera.capture_image(image_name = 'test2',shutter_speed = shutter_speed, awb_gains = awb_gains)



#_____________________Prog__________________________
brick = IBrick()
#msg = b.read_port_raw( Port.One )
#msg = b.read_port( Port.One )

brick.set_mode(Port.A, MotorMode.Degrees)
brick.set_mode(Port.Four, ColorMode.Color)
#
# b.turn_motor_at_power(Port.A, power=15)
# color = b.read_port(Port.Four).sivalue
# print(color)

NumPictures = 25
degAll = 360
Pow = 70

degStage = int(degAll/NumPictures)
for i in range(NumPictures):
   
    # time.sleep(4)


    # image = camera.capture_image()
    #-----------------------------
    camera.capture_image(image_name = "test" +str(i),  folder_name = "pictures")


    # ret = brick.step_motor_at_power(Port.A, power=Pow, steps=degStage*56) #gear ratio 1:56
    ret = brick.step_motor_at_power_wait_for_completion(Port.A, power=Pow, steps=degStage*56) #gear ratio 1:56
    print('end')


    # color = brick.read_port(Port.Four).sivalue
    # if color == ColorSensorColor.Green:

    #     brick.turn_motor_at_power(Port.D,power = 0)
    #     brick.stop_motor(Port.A)
    #     break
