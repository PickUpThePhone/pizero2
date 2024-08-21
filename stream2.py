from flask import Flask, Response
import cv2 as cv
from tennis_detect import tennis_detector
import time

class stream_capture:
    def __init__(self, cap, port=8080): 
        self.cap = cap
        self.port = port
        self.app = Flask(__name__)
        self.app_route()
        self.tennis_detector = tennis_detector(length_filter=30, remove_div_points = 8, random_points=20, threshold=4)

    def encode_frame(self, frame):
        success, buffer = cv.imencode('.jpg', frame)
        if not success:
            print("Failed to encode")
            return None, False
        return buffer.tobytes(), True

    def app_route(self):
        @self.app.route('/')
        def index():
            print("Page requested")
            return '''
            <!doctype html>
            <html>
            <body>
                <h1>Video Feed</h1>
                <img src="/video_feed">
            </body>
            </html>
            '''
        
        @self.app.route('/video_feed')
        def video_feed():
            frame_packet = self.generate_frame()
            return Response(frame_packet, mimetype='multipart/x-mixed-replace; boundary=frame')

    def draw_shapes(self, frame, C, R):
        for i in range(len(R)):
            R_int = R[i]
            x,y = C[i]
            cv.circle(frame, (x,y), 1, (0,0,255), 8)
            cv.rectangle(frame, (x-R_int, y-R_int), (x + R_int, y + R_int), (0, 0, 255), 3)
            print('circle number : ', i+1 , 'position ' , x-320, y-240)
        return frame
    
    def generate_frame(self):
        # Example data for circles and radii
        circles = [(320, 240), (400, 300)]  # Modify this based on your use case
        radii = [50, 30]  # Modify this based on your use case

        while True:
            #reduce CPU strain 
            time.sleep(0.02)
            success, frame = self.cap.read()
            if not success:
                print("Could not get frame")
                break
            C,R = self.tennis_detector.detect(frame)
            # draw object detection shapes on the frame
            frame = self.draw_shapes(frame, C, R)
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
