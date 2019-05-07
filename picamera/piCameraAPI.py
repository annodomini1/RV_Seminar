# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 15:42:14 2015

@author: Ziga Spiclin

Python API to the Pi Camera based on simple socket protocol.

"""

import socket
import time
import sys
import struct
import io
from PIL import Image
import os
from fractions import Fraction
import threading 
from queue import Queue
import numpy as np
 
#------------------------------------------------------------------------------
# PI CAMERA INTERFACE CLASS
#------------------------------------------------------------------------------
class IPiCamera:
    """Interface to EV3 brick via socket communication"""
    def __init__(self, address='localhost', port=12000 ):
        self._address = address
        self._port = port
        self._imgport = self._port + int(np.random.randint(1000)) + 1
        
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
    

    def recv_timeout(the_socket, timeout=10):
        """Recieve a message with unknown size"""
        the_socket.setblocking(0)
        total_data=[];data='';begin=time.time()
        while 1:
            #if you got some data, then break after wait sec
            if total_data and time.time()-begin>timeout:
                break
            #if you got no data at all, wait a little longer
            elif time.time()-begin>timeout*2:
                break
            try:
                data=the_socket.recv(8192)
                if data:
                    total_data.append(data)
                    begin=time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        return b''.join(total_data)
        
        
    def recv_size(the_socket):
        """Recieve a message where size is packed at the beginning"""
        #data length is packed into 4 bytes
        total_len=0;total_data=[];size=sys.maxsize
        size_data=sock_data=b'';recv_size=8192
        while total_len<size:
            sock_data=the_socket.recv(recv_size)
            if not total_data:
                if len(sock_data)>4:
                    size_data+=sock_data
                    size=struct.unpack('>i', size_data[:4])[0]
                    recv_size=size
                    if recv_size>524288:recv_size=524288
                    total_data.append(size_data[4:])
                else:
                    size_data+=sock_data
            else:
                total_data.append(sock_data)
            total_len=sum([len(i) for i in total_data ])
        return b''.join(total_data)      
        
        
    def prepare_to_send_size(message):
        """Prepare to send a message by prepending its size"""
        return struct.pack('>i', len(message)) + message
        
    def exchange_messages( self, message ):
        """Exchange message-response over socket interface"""
        # create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        # connect the socket to the port where the server is listening
        server_address = (self._address, self._port)
        print(server_address)
        sock.connect(server_address)
        # set default response
        response = {}
        try:   
            # send data
            print("message: %s" % message)
            #print("IPiCamera.encode_message(message): %s " % IPiCamera.encode_message(message))

            sock.sendall( IPiCamera.prepare_to_send_size(IPiCamera.encode_message(message) ))
#            print("Start receiving...")
            # look for the response   
#            data_bytes = IPiCamera.recv_timeout(sock,10)  
            data_bytes = IPiCamera.recv_size(sock)  
            #data_bytes = sock.recv(1024)       
            # decode message
            #print( "data_bytes: %s" % data_bytes )
            response = IPiCamera.decode_message( data_bytes )
            print( "response: %s" % response )
            
        finally:
            # close socket
            sock.close()
            
            # return response
            return response
            
            
    def fetch_image_thread(self, folder_name, file_name):
        """Start a server for image acquisition"""
        print("Start image server started")        
        
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', self._imgport))
        print('starting listening for image')
        server_socket.listen(0)        
        
        # Accept a single connection and make a file-like object out of it
        connection = server_socket.accept()[0].makefile('rb')
        try:
            while True:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                image_stream.write(connection.read(image_len))
                image_stream.seek(0)
                        
                image = Image.open(image_stream)
            
                #save image
                #delete existing file first
                image_save_file_name = os.path.join(folder_name, file_name.replace('.jpg','') + '.jpg')
                try:
                    os.remove(image_save_file_name)
                except OSError:
                    pass
                image.save(image_save_file_name)
                # Rewind the stream, open it as an image with PIL and do some
                # processing on it
 
        finally:
            connection.close()
            server_socket.close()        
        
        return
        
        
        
    def start_image_fetch_thread(self, message, queue_return):
        """Send the message to fetch the image"""
        print("Start image fetch started")
        time.sleep(2)
        returnMessage = IPiCamera.verify_message( self.start_image_fetch_thread.__name__, \
            self.exchange_messages( message ) )   
            
        queue_return.put(returnMessage)
        return


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
        

    #--------------------------------------------------------------------------
    # CAMERA FUNCTIONS
    #--------------------------------------------------------------------------
    
    def calibrate_camera_values( self, ISO = 200, rotation = 270, resolution = (972,1296), framerate=30):
        """calibrate camera and get its values"""
        message = { "function_name" : "calibrate_camera_values", \
                    "ISO" : ISO, \
                    "resolution" : resolution, \
                    "framerate" : framerate, \
                    "rotation" : rotation }
        calibratedValues = IPiCamera.verify_message( self.calibrate_camera_values.__name__, \
            self.exchange_messages( message ) )
        
        calibratedValues["awb_gains"] = tuple(map(float, eval(calibratedValues["awb_gains"])))        
        return calibratedValues
    
    
    
    def capture_image(self, image_name = "test", folder_name = "test", shutter_speed = 30000, \
            awb_gains = (0.8, 1.3), ISO = 200, rotation = 270, framerate = 30, \
            resolution = (972,1296), sharpness=0, contrast=0, brightness=50, saturation=0, \
            zoom = (0.0, 0.0, 1.0, 1.0)):
        """capture image with parameters and save it to a fodler"""
        
        ip_address = socket.gethostbyname(socket.gethostname())
        print("ip address sent to server: %s" % ip_address)

        
        message = { "function_name" : "capture_image", \
                    "shutter_speed" : shutter_speed, \
                    "awb_gains" : awb_gains, \
                    "ISO" : ISO, \
                    "rotation" : rotation, \
                    "resolution" : resolution, \
                    "framerate" : framerate, \
                    "IP" : ip_address, \
                    "port" : self._imgport, \
                    "sharpness" : sharpness, \
                    "contrast" : contrast, \
                    "brightness" : brightness, \
                    "saturation" : saturation, \
                    "zoom" : zoom}       
                    
        #create folder
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)      
            
        returnMessage = {}
        
        queue_return = Queue()
        
        image_server_thread = threading.Thread(target=self.fetch_image_thread, args=(folder_name, image_name))
        send_capture_request_thread = threading.Thread(target=self.start_image_fetch_thread, args=(message, queue_return))
        
        image_server_thread.daemon = True
        send_capture_request_thread.daemon = True
        

        image_server_thread.start()        
        send_capture_request_thread.start()
        
        
        send_capture_request_thread.join()
        image_server_thread.join()
        
        returnMessage = queue_return.get()
        

        if "image" in returnMessage:
            print("image saved")
        else:
            print("failed to capture image")
        
        return returnMessage


    
    
    
    
    
