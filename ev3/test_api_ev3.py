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

b.turn_motor_at_power(Port.A, power=15)

while 1:
    
    color = b.read_port(Port.Four).sivalue
    print(color)
    time.sleep(0.001)
    
    if color == ColorSensorColor.Green:
    
        b.turn_motor_at_power(Port.D,power = 0)
        b.stop_motor(Port.A)
        break

time.sleep(0.001)
b.stop_motor(Port.D)

raise Exception('stop here')


reconstructionSteps = 10

for step in range(reconstructionSteps):

    b.step_motor_at_power(Port.A, power=1, steps = int(2520/reconstructionSteps), brake=True)
    time.sleep(1)



#b.step_motor_at_power(Port.D, power=100, steps = 2520, brake=True)


#b.step_motor_at_power(Port.D, power=10, steps = 2520)



#b.play_tone()

#b.set_led_pattern( LedPattern.GreenFlash )

#%% test batch commands
#b.step_two_motors_at_power( Port.B, Port.C, -50, 50, 360, 360 )
import time
import ev3

b = IBrick()
# rotate left and right
def make_turn( m_dir = 1, m_power=25, m_steps=360 ):
    b.step_two_motors_at_power( Port.B, Port.C, \
        power=-m_power*m_dir, power2=m_power*m_dir, \
        steps=m_steps, steps2=m_steps, brake=True, brake2=True )

# move lift up and down
def move_zaxis( m_dir = 1 ):
    b.turn_motor_at_power_for_time( Port.D, power=40*m_dir, time_ms=6000 )

# extent and contract arm
def move_arm( m_dir = 1 ):
    b.turn_motor_at_power_for_time( Port.A, power=15*m_dir, time_ms=1750 )
    
#%% FORWARD
#make_turn( m_dir=-1 )
#time.sleep(2)
make_turn( m_dir=1 )
time.sleep(2)   

move_zaxis( m_dir = -1 )

#move_zaxis( m_dir = 1 )
#time.sleep(9)

b.step_motor_at_power( "bc", power=20, steps=750, brake=True )

time.sleep(5)        
move_arm( m_dir = 1 )
time.sleep(3)    
move_arm( m_dir = -1 )
time.sleep(5) 
b.stop_motor(Port.All)

#%% BACKWARD

b.step_motor_at_power( "bc", power=-20, steps=750, brake=True )

time.sleep(5)

#move_zaxis( m_dir = 1 )
b.turn_motor_at_power_for_time( Port.D, power=40, time_ms=5000 )
time.sleep(8)

make_turn( m_dir=-1 )
time.sleep(2)   
b.stop_motor(Port.All)

#b.turn_motor_at_power_for_time( "bc", power=-40, time_ms=2000 )
#b.step_motor_at_power( "bc", power=-30, steps=700, brake=True )


#move_zaxis( m_dir = 1 )
#time.sleep(9)



   

