from inference import get_model
import numpy as np
import supervision as sv
import cv2


class Yolo:
    def __init__(self, model_id, frame_shape = []): 
        self.model = get_model(model_id)
        self.bounding_box_annotator = sv.BoundingBoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        self.frame_shape = frame_shape
        self.detections = []
        # run inference on our chosen image, image can be a url, a numpy array, a PIL image, etc.

    def detect(self,frame):   
        results = self.model.infer(frame)[0]
        self.detections = sv.Detections.from_inference(results)
        return self.detections

    def get_closest(self, detections): 
        # Filter for tennis balls and find the closest one
        closest_ball = None
        min_distance = float('inf')
        frame_center = (self.frame_shape[1] // 2, self.frame_shape[0] // 2)
        for detection in detections:
            # Assuming the label for tennis balls is 'tennis_ball'; adjust as needed
            if detection.label == 'tennis_ball':
                bbox = detection.bbox
                x_center = (bbox[0] + bbox[2]) / 2
                y_center = (bbox[1] + bbox[3]) / 2
                # Compute distance from the center of the frame
                distance = np.sqrt((x_center - frame_center[0])**2 + (y_center - frame_center[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_ball = detection
                    closest_x_center = x_center
                    closest_y_center = y_center
                    closest_radius = np.sqrt((bbox[2] - bbox[0])**2 + (bbox[3] - bbox[1])**2) / 2
            if closest_ball:
                return [closest_x_center, closest_y_center], closest_radius
            else: 
                return [], []
        
    def draw_shapes(self, frame): 
        annotated_image = self.bounding_box_annotator.annotate(
            scene=frame, detections=self.detections)
        annotated_image = self.label_annotator.annotate(
            scene=annotated_image, detections=self.detections)
        return annotated_image