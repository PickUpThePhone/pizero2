import cv2 as cv
import numpy as np
import serial 

class vision: 
    def __init__(self): 
        self.lower_yellow = np.array([29,86,6]) 
        self.upper_yellow = np.array([64,255,255]) 

    def process_frame(self, frame): 
        hsv = cv.cvtColor(self.frame,cv.COLOR_BGR2HSV) 
        mask = cv.inRange(hsv, self.lower_yellow, self.upper_yellow)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        contours, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            c = max(contours, key=cv.contourArea)
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only return the center and radius if it is big enough 
            if radius > 10: 
                return center, radius