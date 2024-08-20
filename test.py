from stream import stream_capture
import cv2

def init_camera():
    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Camera opened successfully at index {index}.")
            return cap
        cap.release()  
    return None

if __name__ == "__main__":
    cap = init_camera()
    if cap:
        stream = stream_capture(cap, port=8080)
        stream.run_sever()
    else: 
        print("Failed to initialise camera [outside of index range?]")
        
    
    