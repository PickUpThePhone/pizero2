import cv2 
import numpy as np
import serial
class vision: 
    def __init__(self):
        self.tennisball_lower_yellow = np.array([27,70,100])
        self.tennisball_upper_yellow = np.array([32,255,255])
        self.box_lower_yellow = np.array([17,117,150])
        self.box_upper_yellow = np.array([23,255,255])

        # Convert the frame to the HSV color space
    def detect_tennisball(self, frame):
        # Define the lower and upper boundaries of the "tennis ball" in the HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.tennisball_lower_yellow, self.tennisball_upper_yellow)
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
        # return nothing if no detections 
        return [],[]


    def detect_box(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.box_lower_yellow, self.box_upper_yellow)
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
        # return nothing if no box detected
        return [],[]
    