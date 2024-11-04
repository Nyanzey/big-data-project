import cv2
import json
import os
from datetime import datetime
from ultralytics import YOLO

# Load the YOLO model
model = YOLO("./models/yolo11x.pt")  # Replace with the path to your YOLO model if custom

def process_video(video_path, output_data, frame_interval):
    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    video_data = {
        "video_name": os.path.basename(video_path),
        "video_path": video_path,
        "frames": []
    }
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Only process every `frame_interval` frames
        if frame_index % frame_interval == 0:
            timestamp = frame_index / fps  # Calculate timestamp in seconds
            
            # YOLO detection on the current frame with verbose=False to suppress output
            results = model(frame, verbose=False)
            frame_data = {
                "timestamp": round(timestamp, 2),  # Round to 2 decimal places
                "frame": frame_index,
                "detections": []
            }
            
            for result in results:
                for box in result.boxes:
                    # Convert class number to label name
                    label = model.names[box.cls.item()]
                    detection = {
                        "label": label,
                        "confidence": box.conf.item(),
                        "bbox": box.xyxy.tolist()  # Bounding box coordinates
                    }
                    frame_data["detections"].append(detection)
            
            if (frame_data["detections"]):
                video_data["frames"].append(frame_data)
        
        frame_index += 1  # Increment frame count

    cap.release()
    output_data["videos"].append(video_data)

def save_to_json(output_data, output_file="video_data.json"):
    # Write or append to JSON file
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

def main(video_paths, frame_interval=10):
    # Initialize data structure for JSON storage
    output_data = {
        "processed_date": datetime.now().isoformat(),
        "videos": []
    }

    # Process each video in the provided list
    for video_path in video_paths:
        print(f"Processing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
        video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps  # Video length in seconds

        # Calculate frame interval: longer videos get higher intervals
        if video_length > 600:  # For videos longer than 10 minutes
            frame_interval = int(fps * 10)  # Process every 10 seconds
        elif video_length > 300:  # For videos between 5 and 10 minutes
            frame_interval = int(fps * 5)  # Process every 5 seconds
        else:  # For shorter videos
            frame_interval = int(fps * 2)  # Process every 2 seconds

        process_video(video_path, output_data, frame_interval)

    # Save output to JSON
    save_to_json(output_data)

if __name__ == "__main__":
    # List of video paths to process
    video_paths = [
        "./input/bruh.mp4",
        "./input/op3.mp4"
    ]
    
    frame_interval = 100
    main(video_paths, frame_interval)
