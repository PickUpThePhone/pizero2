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
        x, y = self.C
        # Draw the circle around the detected object
        cv.circle(frame, (int(x), int(y)), int(self.R), (0, 255, 255), 2)
        # Draw the center of the detected object
        cv.circle(frame, self.C, 5, (0, 0, 255), -1)
        return frame

     
    def generate_object_coordinates(self):
        lower_yellow = np.array([29,86,6]) 
        upper_yellow = np.array([64,255,255]) 
        while True:
            success, frame = self.cap.read()
            if not success: 
                break
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            mask = cv.inRange(hsv, lower_yellow, upper_yellow)
            mask = cv.erode(mask, None, iterations=2)
            mask = cv.dilate(mask, None, iterations=2)
            contours, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            
            if len(contours)>0:
                c = max(contours, key=cv.contourArea)
                ((x, y), radius) = cv.minEnclosingCircle(c)
                M = cv.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if radius > 10:
                    self.C = center
                    self.R = radius
            time.sleep(0.1) 

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
            time.sleep(0.02)
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
            x,y = self.C
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
                        
        
        
            
            
            
        
