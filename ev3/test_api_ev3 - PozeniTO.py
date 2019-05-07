# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 10:09:08 2015

@author: Ziga Spiclin
"""

from ev3API import *
import time

b = IBrick()
#msg = b.read_port_raw( Port.One )
#msg = b.read_port( Port.One )

b.set_mode(Port.A, MotorMode.Rotations)
b.set_mode(Port.Four, ColorMode.Color)
#
# b.turn_motor_at_power(Port.A, power=15)
#
# while 1:
#
#     color = b.read_port(Port.Four).sivalue
#     print(color)
#     time.sleep(0.001)
#
#     if color == ColorSensorColor.Green:
#
#         #b.turn_motor_at_power(Port.D,power = 0)
#         b.stop_motor(Port.A)
#         break

#65:1 razmerje

# b.set_mode(Port.A, MotorMode.Degrees)
# b.turn_motor_at_power(Port.A, power=15)

degStage = 360
b.step_motor_at_power(Port.A, power=70, steps=degStage*56)