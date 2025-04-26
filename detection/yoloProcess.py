import cv2
import json
import os
from datetime import datetime
from ultralytics import YOLO
import detection.sampleFrames as sampler

# Load the YOLO model
model = YOLO("./models/yolo11x.pt")  # Replace with the path to your YOLO model if custom

def process_video(video_path, output_data, frame_indices):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    video_data = {
        "video_name": os.path.basename(video_path),
        "video_path": video_path,
        "frames": []
    }

    # Process frames lazily
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()

        if not ret:
            continue

        timestamp = round(frame_index / fps, 2)  # Calculate and round timestamp in seconds
        
        # Run YOLO detection on the current frame
        results = model.predict(frame, verbose=False)
        detections = []  # Collect detections for this frame only

        for result in results:
            for box in result.boxes:
                # Convert class number to label name
                label = model.names[box.cls.item()]
                detection = {
                    "label": label,
                    "confidence": box.conf.item(),
                    "bbox": [coord for coord in box.xyxy.tolist()]  # Round coordinates for compactness
                }
                detections.append(detection)

        # Append frame data only if there are detections
        if detections:
            video_data["frames"].append({
                "timestamp": timestamp,
                "frame": frame_index,
                "detections": detections
            })

    cap.release()
    output_data["videos"].append(video_data)

def save_to_json(output_data, output_file="video_data.json"):
    # Use lazy loading for the JSON file if it exists
    existing_data = {"videos": []}

    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_data = json.load(f)

        # Avoid reprocessing videos by checking paths
        processed_video_paths = {video["video_path"] for video in existing_data["videos"]}
        new_videos = [video for video in output_data["videos"] if video["video_path"] not in processed_video_paths]

        if new_videos:
            existing_data["videos"].extend(new_videos)
            existing_data["processed_date"] = datetime.now().isoformat()

    else:
        # Initialize new data if file doesn't exist
        existing_data["videos"] = output_data["videos"]
        existing_data["processed_date"] = datetime.now().isoformat()

    # Save data back to file
    with open(output_file, "w") as f:
        json.dump(existing_data, f, indent=4)

    return existing_data