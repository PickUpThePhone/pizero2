from flask import Flask, Response
import cv2 as cv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def init_camera():
    # Open the camera; try to use index 0 (default) and handle different indices
    for index in range(10):  # Try up to 10 indices to find a working camera
        cap = cv.VideoCapture(index)
        if cap.isOpened():
            logging.info(f"Camera opened successfully at index {index}.")
            return cap
        cap.release()  # Release if not successful
    logging.error("Cannot open any camera. Check if the camera is connected and accessible.")
    return None

cap = init_camera()

def get_frame():
    if cap is None:
        logging.error("Camera not initialized.")
        return None, False
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture image from camera.")
        return None, False
    return frame, True

def encode_frame(frame):
    if frame is None:
        logging.error("No frame to encode.")
        return None, False
    ret, buffer = cv.imencode('.jpg', frame)
    if not ret:
        logging.error("Failed to encode image.")
        return None, False
    return buffer.tobytes(), True

@app.route('/video_feed')
def video_feed():
    logging.debug("Video feed requested.")

    def generate_frames():
        while True:
            frame, success = get_frame()
            if not success:
                logging.error("Failed to get frame. Skipping...")
                continue

            frame_encoded, success = encode_frame(frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
            else:
                logging.error("Failed to encode frame for streaming.")

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    logging.debug("Index page requested.")
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
    logging.info("Starting Flask server.")
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)  # use_reloader=False to avoid conflicts with Flask reloader

if __name__ == '__main__':
    try:
        logging.info("Starting script.")
        stream_camera_feed()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if cap is not None:
            cap.release()
            logging.info("Released camera.")
        logging.info("Finished script execution.")

