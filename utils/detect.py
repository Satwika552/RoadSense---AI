# utils/detect.py
# This is the BRAIN of RoadSense AI — detects road damage using YOLOv8

from ultralytics import YOLO
import cv2
import os
import uuid

# Load YOLOv8 model (uses pretrained model first, we'll fine-tune later)
model = YOLO("yolov8n.pt")  # Auto-downloads on first run (~6MB)

# Damage class names (from RDD2022 dataset)
DAMAGE_CLASSES = {
    0: "Longitudinal Crack",
    1: "Transverse Crack",
    2: "Alligator Crack",
    3: "Pothole"
}

def detect_damage(image_path):
    """
    Takes an image path, runs YOLOv8 detection,
    draws bounding boxes, saves result image,
    returns detection results.
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return None, []

    # Run detection
    results = model(image_path, conf=0.25)  # 25% confidence threshold

    detections = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])

            # Get damage type
            damage_type = DAMAGE_CLASSES.get(class_id, "Road Damage")

            # Calculate severity based on bounding box area
            box_area = (x2 - x1) * (y2 - y1)
            img_area = img.shape[0] * img.shape[1]
            area_ratio = box_area / img_area

            if area_ratio > 0.05:
                severity = "Severe"
                color = (0, 0, 255)      # Red
            elif area_ratio > 0.02:
                severity = "Moderate"
                color = (0, 165, 255)    # Orange
            else:
                severity = "Minor"
                color = (0, 255, 0)      # Green

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{damage_type} | {severity} | {confidence:.0%}"
            cv2.putText(img, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            detections.append({
                "type": damage_type,
                "severity": severity,
                "confidence": f"{confidence:.0%}",
                "location": f"({x1},{y1}) to ({x2},{y2})"
            })

    # Save result image with unique name
    result_filename = f"result_{uuid.uuid4().hex[:8]}.jpg"
    result_path = os.path.join("static", "uploads", result_filename)
    cv2.imwrite(result_path, img)

    return result_filename, detections