import cv2
from stream import stream_frame


# initialise camera in this way because i was having problems with the camera not always existing at video0 index. 
def camera_capture():
    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Camera opened successfully at index {index}.")
            return cap
        cap.release()  
    return None
    
if __name__ == '__main__':


    cap = camera_capture()
    # check if camera captured
    if not cap:
        print("Could not capture. Camera didn't initialise correctly?")
        exit(1)
    # continuously get new frames and serve them 
    stream = stream_frame(frame=None, port=8080)
    while True:  
        success, frame = cap.read()
        if not success:
            print("Could not get frame")
            break 
        stream.update_frame(frame)
    