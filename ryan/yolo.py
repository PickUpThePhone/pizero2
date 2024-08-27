import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient
from io import BytesIO

class Yolo:
    def __init__(self, api_url="https://detect.roboflow.com", api_key="JKeSXyTNdvUIJDdThDP3"):
               
            self.CLIENT = InferenceHTTPClient(api_url, api_key)
            self.MODEL_ID = "tennis-ball-detection-qtrus/2"

    def get_inference(self,frame):
        """Send the image to RoboFlow API for inference using the InferenceHTTPClient."""
        # Convert image to bytes
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        # Use InferenceHTTPClient to send the image for inference
        result = self.CLIENT.infer(image=BytesIO(img_bytes), model_id=self.MODEL_ID)
        
        # Return the result
        return result

    def extract_largest_ball(self, result):
        """Extract the center and radius of the largest tennis ball from the result."""
        if 'predictions' not in result:
            print("No predictions found.")
            return None, None
        
        # Extract predictions
        predictions = result['predictions']
        
        # Initialize variables to track the largest ball
        largest_area = 0
        largest_ball = None

        for prediction in predictions:
            # Extract bounding box coordinates
            x_center = prediction['x']
            y_center = prediction['y']
            width = prediction['width']
            height = prediction['height']
            
            # Calculate the area of the bounding box
            area = width * height
            
            # Update largest ball if this one is larger
            if area > largest_area:
                largest_area = area
                largest_ball = prediction
        
        if largest_ball is None:
            print("No tennis balls detected.")
            return None, None
        
        # Calculate the center and radius of the largest ball
        x_center = largest_ball['x']
        y_center = largest_ball['y']
        radius = max(largest_ball['width'], largest_ball['height']) / 2
        
        return (x_center, y_center), radius