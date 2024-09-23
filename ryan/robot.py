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
        # init
        l_count = 0
        r_count = 0 
        f_count = 0
        # counter for num instances a ball has been detected in a row
        inst = 0
        image_center_threshold = 120 
        while True: 


            #If there is at least one ball detected 
            if len(self.R)>0:
                inst+=1
                # get the radius of the closest ball (by default only the closest is saved in this array)
                radius = self.R[0]
                # get ball center x coordinate
                center_x, _ = self.C[0]
                # get pixel dist from center 
                dist_from_center = center_x - 320
                
                #======================================================================
                
                # If the ball is far away: (determined by a small ball radius)
                if (radius < 140):
                    image_center_threshold = 120 
                # if the ball is in medium distance 
                elif (140 <= radius < 200): 
                    image_center_threshold = 30
                # if the ball is close (radius larger than 200 pixels)
                else: 
                    # stop immediately 
                    stop = "SSSSSSSSSS"
                    self.ser.write(stop.encode('utf-8'))
                    print(f"Ball is close. Halt movement.\n")
                    # restart the loop 
                    continue

                #=====================================================================

                # take a vote between L, R, F commands 
                if dist_from_center < -image_center_threshold:
                    # vote that the robot drives left
                    l_count+=1
                elif dist_from_center > image_center_threshold:
                    # vote that the robot drives right 
                    r_count+=1
                else: 
                    # vote that the robot drives forward 
                    f_count+=1
                
                
                #======================================================================

                # While loop has detected a ball 3 instances in a row, and now the vote takes place on which direction to move
                if inst>=3:
                    # choose the direction that has the highest votes 
                    counts = [l_count, r_count, f_count]
                    directions = ["LLLLLLLLLL", "RRRRRRRRRR", "FFFFFFFFFF"]
                    max_idx = counts.index(max(counts))
                    direction = directions[max_idx]
                    # drive toward that direction  
                    self.ser.write(direction.encode('utf-8')) #send the command over UART to the STM
                    print(direction)


            # ================================================================================================
            # CURRENTLY THIS TELLS THE ROBOT TO STOP WHEN THERE IS NO BALL DETECTED. WE WILL NEED TO DECIDE WHAT HAPPENS WHEN IT CANT SEE ANYTHING
            else:
                stop = "SSSSSSSSSS"
                self.ser.write(stop.encode('utf-8'))
                print(f"No ball detected")

            #=====================================================
            # sleep for 20ms to save resources 
            time.sleep(0.02)