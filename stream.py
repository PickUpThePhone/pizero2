from flask import Flask, Response
import cv2 as cv


class stream_capture:
    def __init__(self, cap, port=8080): 
        self.cap = cap
        self.port = port
        self.app = Flask(__name__)
        self.app_route()

    def encode_frame(self,frame):
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

    def generate_frame(self):
        while True:
            success,frame = self.cap.read()
            if not success:
                print("Could not get frame")
                break
            else: 
                frame_encoded, success = self.encode_frame(frame)
                if success:
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
                else:
                    print("Could not generate frame packet")


    def run_server(self):
        print("Starting server")
        self.app.run(host='0.0.0.0', port=self.port)  

