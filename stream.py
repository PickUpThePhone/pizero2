from flask import Flask, Response
import cv2 as cv
import logging



app = Flask(__name__)

def init_camera():
    for index in range(10):
        cap = cv.VideoCapture(index)
        if cap.isOpened():
            print(f"Camera opened successfully at index {index}.")
            return cap
        cap.release()  # Release if not successful
    print("Cannot open camera")
    return None

cap = init_camera()

def get_frame():
    if cap is None:
        print("Camera init failed.")
        return None, False
    ret, frame = cap.read()
    if not ret:
        print("Cannot get frame")
        return None, False
    return frame, True

def encode_frame(frame):
    if frame is None:
        print("No frame to encode")
        return None, False
    ret, buffer = cv.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode")
        return None, False
    return buffer.tobytes(), True

@app.route('/video_feed')
def video_feed():
    print("Video feed requested")

    def generate_frames():
        while True:
            frame, success = get_frame()
            if not success:
                print("Could not get frame")
                continue

            frame_encoded, success = encode_frame(frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
            else:
                print("Could not generate frame packet")

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
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

def stream_camera_feed():
    print("Starting server")
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)  # use_reloader=False to avoid conflicts with Flask reloader

if __name__ == '__main__':
    try:
        print("Attempting to stream camera feed..")
        stream_camera_feed()
    finally:
        if cap is not None:
            cap.release()
            print("Stopped")

