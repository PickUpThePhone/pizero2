<<<<<<< Updated upstream
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
=======
import cv2
import numpy as np
import random
import time

import serial
>>>>>>> Stashed changes

cam_id = 0
use_uart = True
use_ui = False
use_video = False

frame_mod = 15

<<<<<<< Updated upstream
    def draw_shapes(self, frame):
        for i in range(len(self.R)):
            radius = self.R[i]
            x,y = self.C[i]
            cv.circle(frame, (x,y), radius, (0,255,255), 2)
            cv.circle(frame, (x,y), 5, (0,0,255), -1)
            #print("tennis ball detected")
        return frame
    
    def generate_object_coordinates(self):
        while True:
            success,frame = self.cap.read()
            if success: 
                self.C,self.R = self.vision.detect(frame)
                #print(self.C)
                #print(self.R)
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
            time.sleep(0.1)
            success, frame = self.cap.read()
            if not success or frame is None:
                print("Could not get frame. Continuing...")
                continue
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
                radius = self.R[0]
                if radius > 10:
                    x,_ = self.C[0]
                    # define an array of x,y coordinactually need the y coordinate but its good to have as we may need it later
                    # turn robot towards those coordinates
                    direction = "S" # default stop  
                    if x-320 < -self.image_center_threshold:
                        direction = "L"
                    elif x-320 > self.image_center_threshold:
                        direction = "R"
                    else: 
                        direction = "F"     
                    data = ""
                    # I am not sure what the loop is for
                    print(direction)
                    for i in range(10):
                        data += direction
                    self.ser.write(data.encode('utf-8')) #send the command over UART to the STM
                    # wait 
                    time.sleep(0.02) 
            
        
        
            
=======
if use_uart:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)

if __name__ == '__main__':

    vid = cv2.VideoCapture(cam_id)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 1280
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 720

    prev_frame_pos = None
    close_to_ball = False
    s_count = 0
    l_count = 0
    r_count = 0
    f_count = 0
    frame_count = 0
    c_count = 0

    if use_video:
        video_path = 'indoor_pic/4.mp4'
        vid = cv2.VideoCapture(video_path)

    while True:
        data = "SSSSSSSSSSSSSS"
        ret, frame = vid.read()
        #frame = cv2.imread('indoor_pic/3.jpg')
        if close_to_ball:
            print("adjusting...")

        if not ret:
            if use_video:
                vid = cv2.VideoCapture(video_path)
            else: 
                vid = cv2.VideoCapture(cam_id)
                vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 1280
                vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 720

            ret, frame = vid.read()
        #frame = cv2.imread('indoor_pic/8.jpg')

        # Define the lower and upper boundaries of the "tennis ball" in the HSV color space
        lower_yellow = np.array([22, 47, 50])
        upper_yellow = np.array([60, 200, 255])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bottom_half = []
        if len(contours) > 0:
            # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            #c = max(contours, key=cv2.contourArea)
            bottom_half = []
            for c in contours:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if y > 260: 
                    if radius > 1:
                        bottom_half.append(c)

        if bottom_half:
            c = max(bottom_half, key=cv2.contourArea)
            M = cv2.moments(c)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            ignore = False
            #print(radius)
            if prev_frame_pos is not None:
                x_old, y_old = prev_frame_pos
                dist = np.sqrt((x_old - x)**2 + (y_old -y)**2)

                if dist > 15 or dist == 0:
                    ignore = True
            prev_frame_pos = (x,y)
            if use_ui and not ignore:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
>>>>>>> Stashed changes
            
            	#print(radius)    
                if radius > 200:
            	    print("close but not stopping")
            
            if use_uart and not ignore:
                if close_to_ball:
                    image_center_threshold = 30
                else:
                    image_center_threshold = 120
                direction = "S"
                if x-320 < -image_center_threshold:
                    direction = "L"
                    l_count += 1
                elif x-320 > image_center_threshold:
                    direction = "R"
                    r_count += 1
                else:
                    if not close_to_ball:
                        if radius > 140:
                            direction = "C"
                            print("CLOSE!!!!!")
                            c_count += 1
                        else:
                            direction = "F"
                            f_count += 1
                    else:
                        direction = "W"
                data = ""
                for i in range(10):
                    data += direction
        
        if use_uart:
            frame_count+=1

            if data[0] == "S":
                s_count+=1

            if c_count >= 3:
                close_to_ball = True
            
            if frame_count == frame_mod and not close_to_ball:
                frame_count = 0
                counts = [s_count, f_count, l_count, r_count, c_count]
                most_common = np.argmax(counts)
                datas = ["SSSSSSSSSS", "FFFFFFFFFF", "LLLLLLLLLL", "RRRRRRRRRR", "CCCCCCCCCC"]
                
                data = datas[most_common]

                s_count = 0
                f_count = 0
                l_count = 0
                r_count = 0
                c_count = 0

                ser.write(data.encode('utf-8'))
                print(data[0])
                
                if data[0] == "C":
                    close_to_ball = True

            if close_to_ball:
                ser.write(data.encode('utf-8')) #send the command over UART to the STM
                ser.write(data.encode('utf-8'))
                ser.write(data.encode('utf-8'))
                print(data[0])
                if data[0] == "W":
                    print("Reached the END!!")
                    break

        #print(x-320,y)
        if use_ui:
            cv2.imshow("Frame", frame)
            cv2.imshow("mask", mask)
        #cv2.moveWindow('Original', x_offset * 2-150, y_offset * 2)
        #time.sleep(0.05)

        if use_ui:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

