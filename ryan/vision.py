import cv2 
import numpy as np
import serial

class vision: 
    def __init__(self):
        self.lower_yellow = np.array([17,117,150])
        self.upper_yellow = np.array([23,255,255])
        # Convert the frame to the HSV color space

    def detect(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, np.ones((5, 5)), iterations=2)
        height, width = mask.shape[:2]
        mask[:height//4 , :] = 0
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bottom_half = []
        if len(contours) > 0:
            # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            #c = max(contours, key=cv2.contourArea)
            bottom_half = []
            for c in contours:
                
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                x, y, w, h = cv2.boundingRect(c)
                if w > width//10:
                    bottom_half.append(c)

        if bottom_half:
            c = max(bottom_half, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            center = int(x+w/2),int(y+h/2)

        return [center], [radius]

