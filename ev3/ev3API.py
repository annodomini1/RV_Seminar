# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 15:42:14 2015

@author: Ziga Spiclin

Python API to the EV3 brick based on simple socket protocol.

"""

import socket
import time
from enum import Enum

#------------------------------------------------------------------------------
# GENERAL EV3 ENUMS
#------------------------------------------------------------------------------    
class Port(Enum):
    """Enumeration of ports"""
    A = 'a'; B = 'b'; C = 'c'; D = 'd'
    One = '1'; Two = '2'; Three = '3'; Four = '4'

class BrickButton(Enum):
    NoButton = 0
    Up = 1
    Enter = 2
    Down = 3    
    Right = 4
    Left = 5
    Back = 6
    Any = 7

class LedPattern(Enum):
    Black = 0
    Green = 1
    Red = 2
    Orange = 3
    GreenFlash = 4    
    RedFlash = 5
    OrangeFlash = 6
    GreenPulse = 7
    RedPulse = 8
    OrangePulse = 9

class Color(Enum):
    Background = 0
    Foreground = 1

class FontType(Enum):
    Small = 0
    Medium = 1
    Large = 2

#------------------------------------------------------------------------------
# SENSOR MODE ENUMS
#------------------------------------------------------------------------------    
class TouchMode(Enum):
    Touch = 0    
    Bumps = 1
   
class MotorMode(Enum):
    Degrees = 0
    Rotations = 1
    Percent = 2

class ColorMode(Enum):
    Reflective = 0    
    Ambient = 1
    Color = 2
    ReflectiveRaw = 3
    ReflectiveRgb = 4    
    Calibration = 5

class UltrasonicMode(Enum):
    Centimeters = 0
    Inches = 1
    Listen = 2
    SiCentimeters = 3
    SiInches = 4
    DcCentimeters = 5
    DcInches = 6

class GyroscopeMode(Enum):
    Angle = 0
    Rate = 1
    Fas = 2
    GandA = 3
    Calibrate = 4
    
class InfraredMode(Enum):
    Proximity = 0
    Seek = 1
    Remote = 2
    RemoteA = 3
    SAlt = 4
    Calibrate = 5

#------------------------------------------------------------------------------
# COLOR SENSOR SPECIFIC ENUMS
#------------------------------------------------------------------------------    
class ColorSensorColor(Enum):
    Transparent = 0
    Black = 1
    Blue = 2
    Green = 3
    Yellow = 4
    Red = 5
    White = 6
    Brown = 7

#------------------------------------------------------------------------------
# PORT STATUS INTERFACE CLASS
#------------------------------------------------------------------------------
class IPortStatus:
    """Port status variables"""
    port_index = 0
    device_type = 0
    # device_name = 0 # equal to 'port_index'
    device_mode = 0
    raw_value = 0
    sivalue = 0
    percentage_value = 0
    """Constructor from message"""
    def __init__(self, message):
        self.port_index = IBrick.map_port( message["port_index"] )
        self.device_type = message["device_type"]
        # self.device_name = message["device_name"]
        self.device_mode = IBrick.map_mode( self.device_type, message["device_mode"] )
        self.raw_value = float( message["raw_value"].replace(",", ".") )
        self.sivalue = float( message["sivalue_value"].replace(",", ".") )
        self.percentage_value = float( message["percentage_value"].replace(",", ".") )
        
        if self.device_mode == ColorMode.Color:
            self.sivalue = ColorSensorColor( int(self.sivalue) )

#------------------------------------------------------------------------------
# EV3 BRICK INTERFACE CLASS
#------------------------------------------------------------------------------
class IBrick:
    """Interface to EV3 brick via socket communication"""
    def __init__(self, address='localhost', port=11000 ):
        self._address = address
        self._port = port
        
    #--------------------------------------------------------------------------
    # SOCKET COMMUNICATION PROTOCOL
    #--------------------------------------------------------------------------
    def decode_message( data_bytes, encoding='utf-8', terminator = '<EOF>', \
        linesplit = '\n', keyvaluesplit = ':' ):
        """Decode message in the form of binary data into a key-value dictionary"""
        if not data_bytes: return {}
        data_utf8 = data_bytes.decode(encoding);
        data_utf8 = data_utf8.replace(terminator,'')
        if data_utf8[-1:]==linesplit: data_utf8 = data_utf8[:-1]
        mydict = dict((k.strip(), v.strip()) for k,v in 
                      (item.split(keyvaluesplit) for item in data_utf8.split(linesplit)))
        return mydict
    
    def encode_message( data_dict, encoding='utf-8', terminator = '<EOF>', \
        linesplit = '\n', keyvaluesplit = ':' ):
        """Encode message in the form of key-value dictionary into a  binary data"""
        data_bytes = ""    
        for key in data_dict:
            data_bytes += "%s %s %s %s" % \
                (key, keyvaluesplit, data_dict[key], linesplit)
        data_bytes += terminator          
        data_bytes = data_bytes.replace(" ","")
        return bytes(data_bytes, encoding)
    
    def exchange_messages( self, message, address='localhost', port=11000 ):
        """Exchange message-response over socket interface"""
        # create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        # connect the socket to the port where the server is listening
        server_address = (self._address, self._port)
        sock.connect(server_address)
        # set default response
        response = {}
        try:   
            # send data
#            print("message: %s" % message)
#            print("IBrick.encode_message(message): %s " % IBrick.encode_message(message))
            sock.sendall( IBrick.encode_message(message) )
#            print("Start receiving...")
            # look for the response   
            data_bytes = sock.recv(1024)    
            # decode message
#            print( "data_bytes: %s" % data_bytes )
            response = IBrick.decode_message( data_bytes )
#            print( "response: %s" % response )
        finally:
            # close socket
            sock.close()
            
            # return response
            return response        
    
    #--------------------------------------------------------------------------
    # HELPER FUNCTIONS
    #--------------------------------------------------------------------------    
    def verify_message( fname, message ):
        """Print error and warning messages"""
        if "error" in message.keys():
            print("Error in %s: %s" % (fname, message["error"]) )
        if "warning" in message.keys():
            print("Warning in %s: %s" % (fname, message["warning"]) )
        return message
        
    def get_enum_value( enum_value ):
        """Convert enum to value"""
        if isinstance(enum_value,Enum):        
            value = enum_value.value
        elif isinstance( enum_value, (float, bool)):
            value = int(enum_value)
        else:
            value = enum_value
        return value
    
    def map_port( port ):
        """Map different port markups to corresponding enum"""
        value = None
        try:
            pmap = { 'one':Port.One, '1':Port.One, \
                     'two':Port.Two, '2':Port.Two, \
                     'three':Port.Three, '3':Port.Three, \
                     'four':Port.Four, '4':Port.Four, \
                     'a':Port.A, 'b':Port.B, \
                     'c':Port.C, 'd':Port.D }
            key = str( port ).lower()
            value = pmap[ key ]
        finally:
            return value
    
    def map_mode( device_type, device_mode ):
        """Map device mode according to device type"""
        # default value    
        value = None
        try:
            # get mode value
            dm = int(device_mode)    
            # build map
            mmap = { 'color': ColorMode, \
                     'touch': TouchMode, \
                     'motor': MotorMode, \
                     'lmotor': MotorMode, \
                     'mmotor': MotorMode, \
                     'ultrasonic': UltrasonicMode, \
                     'infrared' : InfraredMode, \
                     'gyroscope' : GyroscopeMode }
            key = str( device_type ).lower()
            value = mmap[ key ](dm)        
        finally:
            return value        

    #--------------------------------------------------------------------------
    # GENERAL I/O FUNCTIONS
    #--------------------------------------------------------------------------
    def read_port_raw( self, port ):
        """Read the input/output port raw"""
        message = { "function_name" : "get_inputport()", \
                    "port_index"    : IBrick.get_enum_value(port) }    
        return IBrick.verify_message( self.read_port_raw.__name__, \
            self.exchange_messages( message ) )    
    
    def read_port( self, port ):
        """Read the input/output port and return port status"""
        return IPortStatus( self.read_port_raw( port ) )
    
    def set_mode( self, port, mode ):
        """Step motor at power (0-100), steps (degrees), brake(T/F)"""
        message = { "function_name" : "set_inputport()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "device_mode" : IBrick.get_enum_value(mode) }   
        return IBrick.verify_message( self.set_mode.__name__, \
            self.exchange_messages( message ) )    
    
    #--------------------------------------------------------------------------
    # MOTOR CONTROL FUNCTIONS
    #--------------------------------------------------------------------------
    def step_motor_at_power( self, port, power=10, steps=0, brake=False  ):
        """Step motor at power (0-100), steps (degrees), brake(T/F)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "StepMotorAtPowerAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "power" : power, \
                    "steps" : steps, \
                    "brake" : brake }   
        return IBrick.verify_message( self.step_motor_at_power.__name__, \
            self.exchange_messages( message ) ) 
 
    def step_motor_at_power_wait_for_completion( self, port, power=10, steps=0, brake=False  ):
        """Step motor at power (0-100), steps (degrees), brake(T/F)"""
        message_motor_turn = { "function_name" : "set_outputport()", \
                    "motor_fname" : "StepMotorAtPowerAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "power" : power, \
                    "steps" : steps, \
                    "brake" : brake }

        # set mode that returns steps
        current_mode = self.read_port(port).device_mode
        self.set_mode(port, MotorMode.Degrees)        
        
        motor_steps_start = self.read_port(port).sivalue
        motor_steps_end = motor_steps_start           
        return_message = {}
 
        motor_moved = False
        start_time = time.time()

        while motor_moved == False:
            # move motor
            return_message = IBrick.verify_message( self.step_motor_at_power.__name__, \
                self.exchange_messages( message_motor_turn ) )

            while True:
                time.sleep(0.2)

                motor_steps_end = self.read_port(port).sivalue
                # check if the motor moved and completed enough rotations
                #check difference in steps if it is achieved
                if abs(motor_steps_end-motor_steps_start) > steps*0.9:
                    motor_moved = True
                    break
                
                end_time = time.time()
                # motor failed to move -> move it again
                #print("Time %s, Steps %s" % ((end_time - start_time), abs(motor_steps_end-motor_steps_start)))
                if ((end_time - start_time) > 5) and (abs(motor_steps_end-motor_steps_start) < 0.1 * steps):
                    self.stop_motor( port, brake=True )
                    time.sleep(0.2)
                    motor_moved = False
                    start_time = time.time()
                    print('Motor failed to move! Retrying.')
                    break
        
        #while abs(self.read_port(port).sivalue-motor_steps_start) < steps*0.98:
        #    time.sleep(0.3)    
        
        if abs(self.read_port(port).sivalue-motor_steps_start) > 1.5 * steps:
            print('Motor made two turns!')
            
        self.set_mode(port, current_mode)
        time.sleep(0.1)
        
        return return_message
        
            
   
    def turn_motor_at_power_with_check( self, port, power=10 ):
        """Turn motor at power (0-100)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "TurnMotorAtPowerAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "power" : power }   
        
        current_mode = self.read_port(port).device_mode
        self.set_mode(port, MotorMode.Degrees)        
        
        motor_steps_start = 0
        motor_steps_end = 0
        
        while abs(motor_steps_start-motor_steps_end) == 0:
            motor_steps_start = self.read_port(port).sivalue                   
            return_msg = IBrick.verify_message( self.turn_motor_at_power.__name__, \
                self.exchange_messages( message ) )
            time.sleep(0.1)
            motor_steps_end = self.read_port(port).sivalue
            
        self.set_mode(port, current_mode)
        time.sleep(0.1)
        return return_msg        
        
    def turn_motor_at_power( self, port, power=10 ):
        """Turn motor at power (0-100)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "TurnMotorAtPowerAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "power" : power }   
        return IBrick.verify_message( self.turn_motor_at_power.__name__, \
            self.exchange_messages( message ) )          
    
    def turn_motor_at_power_for_time( self, port, power=10, time_ms=1000, brake=False ):
        """Turn motor at power (0-100) for time in miliseconds, brake(T/F)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "TurnMotorAtPowerForTimeAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "power" : power, \
                    "time_ms" : time_ms, \
                    "brake" : brake }                   
        return_msg = IBrick.verify_message( self.turn_motor_at_power_for_time.__name__, \
            self.exchange_messages( message ) )
        time.sleep(float(time_ms)/1000.0+0.25)
        return return_msg
    
    def stop_motor_with_check( self, port, brake=True ):
        """Stop motor, brake(T/F)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" :  "StopMotorAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "brake" : brake }
        current_mode = self.read_port(port).device_mode
        self.set_mode(port, MotorMode.Degrees)        
        
        motor_steps_start = 0
        motor_steps_end = 1
        
        while abs(motor_steps_start-motor_steps_end) > 0:
            motor_steps_start = self.read_port(port).sivalue                   
            return_msg = IBrick.verify_message( self.stop_motor.__name__, \
                self.exchange_messages( message ) )
            time.sleep(0.1)
            motor_steps_end = self.read_port(port).sivalue
            
        self.set_mode(port, current_mode)
        time.sleep(0.1)
        return return_msg
    
    def stop_motor( self, port, brake=True ):
        """Stop motor, brake(T/F)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "StopMotorAsync()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "brake" : brake }
                    
        return_msg = IBrick.verify_message( self.stop_motor.__name__, \
            self.exchange_messages( message ) )
        return return_msg    
    
    def step_two_motors_at_power( self, port, port2, \
        power=10, power2=10,                         \
        steps=0,  steps2=0,                          \
        brake=False, brake2=False ):
        """Step motor at power (0-100), steps (degrees), brake(T/F)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "StepMotorAtPowerBatch()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "port_index2" : IBrick.get_enum_value(port2), \
                    "power" : power, \
                    "steps" : steps, \
                    "brake" : brake,
                    "power2" : power2, \
                    "steps2" : steps2, \
                    "brake2" : brake2,
                     }   

        return IBrick.verify_message( self.step_two_motors_at_power.__name__, \
            self.exchange_messages( message ) ) 
    
    def turn_two_motors_at_power( self, port, port2, power=10, power2=10 ):
        """Turn motor at power (0-100)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "TurnMotorAtPowerBatch()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "port_index2" : IBrick.get_enum_value(port2), \
                    "power" : power, \
                    "power2" : power2 }   
        return IBrick.verify_message( self.turn_two_motors_at_power.__name__, \
            self.exchange_messages( message ) ) 
    
    def turn_two_motors_at_power_for_time( self, port, port2, \
            power=10, power2=10,                              \
            time_ms=1000, time_ms2=1000,                      \
            brake=False, brake2=False ):
        """Turn motor at power (0-100) for time in miliseconds, brake(T/F)"""
        message = { "function_name" : "set_outputport()", \
                    "motor_fname" : "TurnMotorAtPowerForTimeBatch()", \
                    "port_index" : IBrick.get_enum_value(port), \
                    "port_index2" : IBrick.get_enum_value(port2), \
                    "power" : power, \
                    "power2" : power2, \
                    "time_ms" : time_ms, \
                    "time_ms2" : time_ms2, \
                    "brake" : brake, \
                    "brake2" : brake2 }                   
        return IBrick.verify_message( self.turn_two_motors_at_power_for_time.__name__, \
            self.exchange_messages( message ) )

    #--------------------------------------------------------------------------
    # SPECIALIZED MODULE FUNCTIONS
    #--------------------------------------------------------------------------
    def play_tone( self, volume=100, frequency=1000, duration_ms=1000 ):
        """Play tone with given volume, frequency and duration in miliseconds"""
        message = { "function_name" : "set_module()", \
                    "module_fname" : "PlayToneAsync()", \
                    "volume" : volume, \
                    "frequency" : frequency, \
                    "duration_ms" : duration_ms }    
        return IBrick.verify_message( self.play_tone.__name__, \
            self.exchange_messages( message ) ) 
              
    def play_sound( self, filename, volume=100 ):
        """Play sound with given filename (file is stored on the EV3 brick)"""
        message = { "function_name" : "set_module()", \
                    "module_fname" : "PlayToneAsync()", \
                    "volume" : volume, \
                    "filename" : filename }    
        return IBrick.verify_message( self.play_sound.__name__, \
            self.exchange_messages( message ) ) 
       
    def clean_ui( self ):
        """Clean user interface (UI) screen on the EV3 brick"""
        message = { "function_name" : "set_module()", \
                    "module_fname" : "CleanUIAsync()" }    
        return IBrick.verify_message( self.clean_ui.__name__, \
            self.exchange_messages( message ) ) 
          
    def clear_changes( self, port ):
        """Clear change events recorded on input ports"""
        message = { "function_name" : "set_module()", \
                    "module_fname" : "ClearChangesAsync()", \
                    "port_index"    : IBrick.get_enum_value(port) }      
        return IBrick.verify_message( self.clear_changes.__name__, \
            self.exchange_messages( message ) )   
          
    def clear_all_devices( self ):
        """Clear all devices settings - restore to default"""
        message = { "function_name" : "set_module()", \
                    "module_fname" : "ClearAllDevicesAsync()" }    
        return IBrick.verify_message( self.clear_all_devices.__name__, \
            self.exchange_messages( message ) )    
          
    def set_led_pattern( self, pattern = LedPattern.Green ):
        """Set LED pattern/color on the EV3 brick"""    
        message = { "function_name" : "set_module()", \
                    "module_fname" : "SetLedPatternAsync()", \
                    "ledpattern"    : IBrick.get_enum_value(pattern) }      
        return IBrick.verify_message( self.set_led_pattern.__name__, \
            self.exchange_messages( message ) )  
