from flask import Flask, Response
import cv2 as cv
from vision import vision
import time
import numpy as np
from serial import Serial

class Robot:
    def __init__(self, cap, port=8080): 
        self.cap = cap
        self.port = port
        self.app = Flask(__name__)
        self.app_route()
        self.vision = vision()
        self.C = []
        self.R = []
        self.image_center_threshold = 20 # so that the turn towards algorithm does not get stuck in an infinite loop 
        self.ser = Serial('/dev/serial0', 9600, timeout=1) # start serial instance for Robot

    def encode_frame(self, frame):
        success, buffer = cv.imencode('.jpg', frame)
        if not success:
            print("Failed to encode")
            return None, False
        return buffer.tobytes(), True

    def app_route(self):
        @self.app.route('/')
        def index():
            print("Page requested")
            return '''
            <!doctype html>
            <html>
            <body>
                <img src="/video_feed">
            </body>
            </html>
            '''
        
        @self.app.route('/video_feed')
        def video_feed():
            frame_packet = self.generate_frame()
            return Response(frame_packet, mimetype='multipart/x-mixed-replace; boundary=frame')

    def draw_shapes(self, frame):
        for i in range(len(self.R)):
            radius = self.R[i]
            x,y = self.C[i]
            cv.circle(frame, (x,y), radius, (0,0,255), 22)
            cv.cicle(frame, (x,y), 5, (0,0,255), -1)
            print("tennis ball detected")
        return frame
    
    def generate_object_coordinates(self):
        while True:
            success,frame = self.cap.read()
            if success: 
                self.C,self.R = self.vision.detect(frame)
            # spam update object coordinates
            
    def cast_frame(self,frame): 
        # Decrease the brightness by subtracting the value
        value = 0
        # Convert the image to float32 to prevent clipping issues
        frame = frame.astype(np.float32)
        # Decrease the brightness by subtracting the value
        frame -= value
        # Clip the values to be in the valid range [0, 255] and convert back to uint8
        frame = np.clip(frame, 0, 255).astype(np.uint8)
        return frame 
        
    
    def generate_frame(self):
        while True:
            #reduce the frame rate significantly to reduce CPU strain. Can do this because it is just  GUI and not important for the robots function
            time.sleep(0.2)
            success, frame = self.cap.read()
            if not success:
                print("Could not get frame")
                break
            # cast the frame into a standard size 
            frame = self.cast_frame(frame)
            # draw the object detection shapes on the frame
            frame = self.draw_shapes(frame)
            #encode the frame 
            frame_encoded, success = self.encode_frame(frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
            else:
                print("Could not generate frame packet")

    def run_server(self):
        print("Starting server")
        self.app.run(host='0.0.0.0', port=self.port)
        
        
    def movement_control(self): 
        while True: 
            if len(self.R)>0: 
                # only if radius is large enough 
                if self.R > 10:
                    x,_ = self.C
                    # define an array of x,y coordinactually need the y coordinate but its good to have as we may need it later
                    # turn robot towards those coordinates
                    direction = "S" # default stop  
                    if x < -self.image_center_threshold:
                        direction = "L"
                    elif x > self.image_center_threshold:
                        direction = "R"
                    else: 
                        direction = "F"     
                    data = ""
                    # I am not sure what the loop is for
                    for i in range(10):
                        data += direction
                    self.ser.write(data.encode('utf-8')) #send the command over UART to the STM
    
            
        
        
            
            
            
        
