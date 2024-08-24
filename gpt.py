import cv2
import numpy as np
import serial

# Define the lower and upper boundaries of the "tennis ball" in the HSV color space
lower_yellow = np.array([29, 86, 6])
upper_yellow = np.array([64, 255, 255])

ser = serial.Serial('/dev/serial0', 9600, timeout=1)

# Start video capture from the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the tennis ball color
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Perform a series of dilations and erosions to remove any small blobs left in the mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Only proceed if at least one contour was found
    if len(contours) > 0:
        # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # Only proceed if the radius meets a minimum size
        if radius > 10:
            # Draw the circle and centroid on the frame
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            #print(x-320,y)
            image_center_threshold = 20
            direction = "S"
            if x-320 < -image_center_threshold:
                direction = "L"
            elif x-320 > image_center_threshold:
                direction = "R"
            else:
                direction = "F"

            data = ""
            for i in range(10):
                data += direction
            ser.write(data.encode('utf-8')) #send the command over UART to the STM

            #print('time used all', time.time() - ts)
            #print(direction)
    # Show the frame to our screen
    cv2.imshow("Frame", frame)

    # If the 'q' key is pressed, break from the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any open windows
cap.release()
cv2.destroyAllWindows()
