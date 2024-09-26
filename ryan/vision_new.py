import cv2 
import numpy as np
import serial

class vision: 
    def __init__(self):
        self.lower_yellow = np.array([27,70,100])
        self.upper_yellow = np.array([32,255,255])
        # Convert the frame to the HSV color space

    def detect(self, frame):

        # Define the lower and upper boundaries of the "tennis ball" in the HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        mask = cv2.erode(mask, np.ones((3, 3)), iterations=1)
        mask = cv2.dilate(mask, np.ones((5, 5)), iterations=1)
        height, width = mask.shape[:2]
        boundary_line = height//6
        mask[:boundary_line, :] = 0
        
        B_mask = np.zeros((height, width), dtype=np.uint8)
        top_left = (int(width * 1/6), int(height * 1/6))
        bottom_right = (int(width * 5/6), int(height * 5/6))
        B_mask[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = 255
        mask = cv2.bitwise_and(B_mask, mask)
        
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bottom_half = []
        if len(contours) > 0:
            # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            #c = max(contours, key=cv2.contourArea)
            bottom_half = []
            for c in contours:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if radius > 10:
                    bottom_half.append(c)

        if bottom_half:
            c = max(bottom_half, key=cv2.contourArea)
            M = cv2.moments(c)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = int(x) , int(y)

        return [center], [radius]

