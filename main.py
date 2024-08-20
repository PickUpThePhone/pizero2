from flask import Flask, Response
import cv2 as cv

app = Flask(__name__)

cap = cv.VideoCapture(0)  

if not cap.isOpened():
    print("Cannot open camera")
    exit()

def get_frame():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        success = False
    else:
        success = True
    return ret, frame, success

def encode_frame(frame):
    ret, buffer = cv.imencode('.jpg', frame)
    if not ret:
        print("Encode failed")
        success = False
        frame_encoded = None
    else:
        frame_encoded = buffer.tobytes()
        success = True
    return frame_encoded, success

@app.route('/video_feed')
def video_feed():
    print("Video feed requested")

    def generate_frames():
        while True:
            ret, frame, success = get_frame()
            if success:
                frame_encoded, success = encode_frame(frame)
                if success:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
                else:
                    print("Encoding failed in streaming")
            else:
                print("Failed to get frame")

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    print("Page Requested")
    return '''
    <!doctype html>
    <html>
    <body>
        <h1>Video Feed</h1>
        <img src="/video_feed">
    </body>
    </html>
    '''

def stream_camera_feed():
    print("Streaming")
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    try:
        print("Starting server")
        stream_camera_feed()
    finally:
        cap.release()
        cv.destroyAllWindows()

