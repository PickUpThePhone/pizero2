from flask import Flask, Response
import cv2 as cv
from tennis_detect import tennis_detector
import time
import numpy as np
from serial import Serial

class Robot:
    def __init__(self, cap, port=8080): 
        self.cap = cap
        self.port = port
        self.app = Flask(__name__)
        self.app_route()
        self.tennis_detector = tennis_detector(length_filter=30, remove_div_points = 8, random_points=20, threshold=4)
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
            R_int = self.R[i]
            x,y = self.C[i]
            cv.circle(frame, (x,y), 1, (0,0,255), 8)
            cv.rectangle(frame, (x-R_int, y-R_int), (x + R_int, y + R_int), (0, 0, 255), 3)
            print('circle number : ', i+1 , 'position ' , x-320, y-240)
        return frame
    
    def generate_object_coordinates(self):
        while True:
            success,frame = self.cap.read()
            if success: 
                self.C,self.R = self.tennis_detector.detect(frame)
                #print(f"C = {self.C}")
                #print(f"R = {self.R}")
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
            if len(self.R)>0: 
                # define an array of x,y coordinates equal to the number of circle center. 
                x = np.zeros(len(self.C))
                y = np.zeros(len(self.C))
                r = np.zeros(len(self.R))
                # step through each circle center and corresponding radius 
                i = 0
                for center, radius in zip(self.C, self.R):
                    # extract the x,y coordinates from center current center
                    x[i] = center[i] # x in the [x,y] value of center
                    # normalise so that x is from -160 to +160 with frame center at 0
                    x[i] = x[i] - 320 
                    # extract radius 
                    r[i] = radius
                    i = i + 1
                # determine the coordinates that correspond to the largest radius 
                max_idx = np.argmax(r)
                x_closest = x[max_idx]
                y_closest = y[max_idx] # we dont actually need the y coordinate but its good to have as we may need it later
                # turn robot towards those coordinates
                direction = "S" # default stop  
                if x_closest < -self.image_center_threshold:
                    direction = "L"
                elif x_closest > self.image_center_threshold:
                    direction = "R"
                else: 
                    direction = "F"     
                data = ""
                # I am not sure what the loop is for
                for i in range(10):
                    data += direction
                self.ser.write(data.encode('utf-8')) #send the command over UART to the STM
                print(f"{direction}")
    
            
        
        
            
            
            
        
