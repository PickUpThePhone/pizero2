from flask import Flask, Response
import cv2 as cv
from tennis_detect import tennis_detector
import time
import numpy as np
from serial import Serial
from vision import vision 

class Robot:
    def __init__(self, cap, port=8080): 
        self.cap = cap
        self.port = port
        self.app = Flask(__name__)
        self.app_route()
        #self.tennis_detector = tennis_detector(length_filter=30, remove_div_points = 8, random_points=20, threshold=4)
        self.vision = vision()
        self.C = None 
        self.frame = cap.read()  
        self.R = None 
        self.x = 0
        self.y = 0
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

    def draw_shapes(self,frane):
        x = self.x 
        y = self.y 
        # Draw the circle around the detected object
        if self.R and self.C is not None: 
            cv.circle(frame, (int(x), int(y)), int(self.R), (0, 255, 255), 2)
            # Draw the center of the detected object
            cv.circle(frame, self.C, 5, (0, 0, 255), -1)
     
    def generate_object_coordinates(self):
        lower_yellow = np.array([29,86,6]) 
        upper_yellow = np.array([64,255,255]) 
        success, frame = self.cap.read()
        self.frame = frame
        while True:
            if not success:
                print("Could not get frame") 
                break
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            mask = cv.inRange(hsv, lower_yellow, upper_yellow)
            mask = cv.erode(mask, None, iterations=2)
            mask = cv.dilate(mask, None, iterations=2)
            contours, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            
            if len(contours)>0:
                c = max(contours, key=cv.contourArea)
                ((self.x, self.y), radius) = cv.minEnclosingCircle(c) # fix this later cos its jank
                M = cv.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if radius > 10:
                    self.C = center
                    self.R = radius
                    return
            else: 
                self.C = None
                self.R = None
                return
            time.sleep(0.1) 

    def cast_frame(self,frame): 
        # Decrease the brightness by subtracting the value
        value = 0
        # Convert the image to float32 to prevent clipping issues
        frame_float = frame.astype(np.float32)
        # Decrease the brightness by subtracting the value
        frame_float -= value
        # Clip the values to be in the valid range [0, 255] and convert back to uint8
        frame_cast = np.clip(frame_float, 0, 255).astype(np.uint8)
        return frame_cast
        
    
    def generate_frame(self):
        while True:
            #reduce the frame rate significantly to reduce CPU strain. Can do this because it is just  GUI and not important for the robots function
            time.sleep(0.02)
            # draw on objects
            frame_shapes = self.draw_shapes(self.frame)
            # cast the frame into a standard size 
            frame_cast = self.cast_frame(frame_shapes)
            # draw the object detection shapes on the frame
            #encode the frame 
            frame_encoded, success = self.encode_frame(frame_cast)
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
            if self.C is not None:
                print(self.C)
                x,y = self.C
                x = x - 320
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
                print(f"{direction}")
                        
        
        
            
            
            
        
