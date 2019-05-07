# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 15:42:14 2015

@author: Ziga Spiclin

Python API to the Pi Camera based on simple socket protocol.

"""

import socket
from piCameraAPI import IPiCamera
import picamera
from fractions import Fraction
import time
import io
import struct

#------------------------------------------------------------------------------
# PI CAMERA INTERFACE CLASS
#------------------------------------------------------------------------------
class IPiCameraServer:
    
    """Interface to EV3 brick via socket communication"""
    def __init__(self, address='localhost', port=12000 ):
        self._address = address
        self._port = port
        
    #--------------------------------------------------------------------------
    # SOCKET COMMUNICATION PROTOCOL
    #--------------------------------------------------------------------------        
    
    def start_server(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        server_address = (self._address, self._port)
        print('starting up on %s port %s' % server_address)
        #sock.bind(server_address)

        sock.bind(server_address)        
        # Listen for incoming connections
        sock.listen(1)
        #connection, client_address = sock.accept()
        
        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = sock.accept()
        
            try:
                print('connection from', client_address)
        
                # Receive the data in small chunks and retransmit it
                #dataBytes = IPiCamera.recv_timeout(connection,10)      
                dataBytes = IPiCamera.recv_size(connection)      
                #dataBytes = connection.recv(1024)                                  
                print(dataBytes)                    
                data = IPiCamera.decode_message(dataBytes)
                print(data)   
                processedData = IPiCameraServer.process_data(data)
                print(processedData)   
                connection.sendall(IPiCamera.prepare_to_send_size(IPiCamera.encode_message(processedData)))
                    
            finally:
                # Clean up the connection
                connection.close()
            
            
    def process_data(message):
        """ process the recieved data from the client  """
        print(message)
        
        if message['function_name'] == 'calibrate_camera_values':
            return IPiCameraServer.calibrate_camera_values( \
                ISO = message.get('ISO',200), \
                rotation = message.get('rotation',90), \
                framerate = message.get('framerate',30), \
                resolution = eval(message.get('resolution',(2592,1944))))
        elif message['function_name'] == 'capture_image':
            return IPiCameraServer.capture_image( \
                shutter_speed = message.get('shutter_speed',30000), \
                awb_gains = eval(message.get('awb_gains',(0.8, 1.3))), \
                ISO = message.get('ISO',200), \
                rotation = message.get('rotation',90), \
                resolution = eval(message.get('resolution',(2592,1944))), \
                framerate = message.get('framerate',30), \
                ip = message.get('IP'), \
                port= message.get('port',13000), \
                sharpness = message.get('sharpness',0), \
                contrast = message.get('contrast',0), \
                brightness = message.get('brightness',50), \
                saturation = message.get('saturation',0), \
                zoom = eval(message.get('zoom',(0.0, 0.0, 1.0, 1.0))))

        return {}            
        
        
    ############################################
    # PI CAMERA FUNCTIONS
    ############################################
        
        
    
    def calibrate_camera_values(ISO = 200, rotation = 90, \
                                resolution = (2592,1944), framerate = 30):
        """calibrate camera values"""
        
        with picamera.PiCamera() as camera:
            camera.resolution = resolution
            camera.framerate = int(framerate)
            camera.ISO = int(ISO)
            camera.rotation = int(rotation)
            
            # Wait for the automatic gain control to settle
            camera.start_preview()
            # Camera warm-up time
            time.sleep(5)            
            
            # Now fix the values
            camera.shutter_speed = camera.exposure_speed
            camera.exposure_mode = 'off'
            g = camera.awb_gains
            camera.awb_mode = 'off'
            camera.awb_gains = g
      
            message = { "shutter_speed" : camera.shutter_speed, \
                    "awb_gains" : g }
        return message
        
        
        
        
    def capture_image(ip = '192.168.32.254', port = 13000, \
                      resolution = (2592,1944), framerate = 30, \
                      shutter_speed = 30000, awb_gains = (0.8,1.3), \
                      ISO = 200, rotation = 90, \
                      sharpness=0, contrast=0, brightness=50, saturation=0, \
                      zoom = (0.0, 0.0, 1.0, 1.0)):
        """captures an image an returns it as a message"""  

        # Connect a client socket to my_server:8000 (change my_server to the
        # hostname of your server)
        client_socket = socket.socket()
        client_socket.connect((ip, int(port)))

        # Make a file-like object out of the connection
        connection = client_socket.makefile('wb')
        try:
            with picamera.PiCamera() as camera:
                
                camera.resolution = resolution
                camera.framerate = int(framerate)
                camera.ISO = int(ISO)
                camera.rotation = int(rotation)
                camera.zoom = zoom
                camera.start_preview()
                # Camera warm-up time
                time.sleep(2)            
                
                camera.exposure_mode = 'off'
                camera.awb_mode = 'off'
                camera.awb_gains = awb_gains   
                camera.shutter_speed = int(shutter_speed)
                
                camera.sharpness = int(sharpness)
                camera.contrast = int(contrast)
                camera.brightness = int(brightness)
                camera.saturation = int(saturation)                

                # Note the start time and construct a stream to hold image data
                # temporarily (we could write it directly to connection but in this
                # case we want to find out the size of each capture first to keep
                # our protocol simple)
                start = time.time()
                stream = io.BytesIO()
                camera.capture(stream, 'jpeg')
                # Write the length of the capture to the stream and flush to
                # ensure it actually gets sent
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                # Rewind the stream and send the image data over the wire
                stream.seek(0)
                connection.write(stream.read())
                # If we've been capturing for more than 30 seconds, quit

                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
            # Write a length of zero to the stream to signal we're done
            connection.write(struct.pack('<L', 0))

            message = {"image" : "captured"}
        finally:
            connection.close()
            client_socket.close()
                
        return message
        
        
        
        
        
        
        
        
        
#            camera parameters
#camera.sharpness = 0
#camera.contrast = 0
#camera.brightness = 50
#camera.saturation = 0
#camera.ISO = 0
#camera.video_stabilization = False
#camera.exposure_compensation = 0
#camera.exposure_mode = 'auto'
#camera.meter_mode = 'average'
#camera.awb_mode = 'auto'
#camera.image_effect = 'none'
#camera.color_effects = None
#camera.rotation = 0
#camera.hflip = False
#camera.vflip = False
#camera.crop = (0.0, 0.0, 1.0, 1.0)
        
        
#         camera parameters lowlight
#camera.resolution = (1280, 720)
## Set a framerate of 1/6fps, then set shutter
## speed to 6s and ISO to 800
#camera.framerate = Fraction(1, 6)
#camera.shutter_speed = 6000000
#camera.exposure_mode = 'off'
#camera.iso = 800
## Give the camera a good long time to measure AWB
## (you may wish to use fixed AWB instead)
#sleep(10)
## Finally, capture an image with a 6s exposure. Due
## to mode switching on the still port, this will take
## longer than 6 seconds
#camera.capture('dark.jpg')
