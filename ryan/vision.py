import cv2 as cv
import numpy as np
import serial

class vision: 
    def __init__(self):
        self.lower_yellow = np.array([29,86,6])
        self.upper_yellow = np.array([64,255,255])
        # Convert the frame to the HSV color space

    def detect(self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, self.lower_yellow, self.upper_yellow)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        contours, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # in case we want to detect multiple obejects in the image later
        center = []        
        radius = []
        # only update radius and center if at least 1 contour was found
        if len(contours) > 0:
            # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            c = max(contours, key=cv.contourArea)
            ((x, y), r) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            # add the radius to list
            center.append([int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])])
            #center.append([int(x),int(y)])
            radius.append(int(r))
        return center, radius
