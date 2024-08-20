from flask import Flask, Response
import cv2 as cv

app = Flask(__name__)

# Try opening the camera and handle potential issues
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

def get_frame():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        return None
    return frame

def encode_frame(frame):
    ret, buffer = cv.imencode('.jpg', frame)
    if not ret:
        print("Encode failed")
        return None
    return buffer.tobytes()

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            frame = get_frame()
            if frame is not None:
                frame_encoded = encode_frame(frame)
                if frame_encoded:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
                else:
                    print("Encoding failed in streaming")
            else:
                print("Failed to get frame")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
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
        # Conditionally destroy windows if supported
        if cv.getBuildInformation().find('GTK') != -1:
            cv.destroyAllWindows()

