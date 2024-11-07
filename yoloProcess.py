import cv2
import json
import os
from datetime import datetime
from ultralytics import YOLO
import sampleFrames as sampler

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
    
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()

        # Only process every `frame_interval` frames
        if ret:
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

    cap.release()
    output_data["videos"].append(video_data)

def save_to_json(output_data, output_file="video_data_yolo.json"):
    # Check if the JSON file exists
    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r") as f:
            existing_data = json.load(f)
        
        # Check if the video has already been processed
        processed_video_paths = {video["video_path"] for video in existing_data["videos"]}
        
        # Append only new videos
        new_videos = [video for video in output_data["videos"] if video["video_path"] not in processed_video_paths]
        if new_videos:
            existing_data["videos"].extend(new_videos)
            existing_data["processed_date"] = datetime.now().isoformat()
        
        # Save the updated data back to the file
        with open(output_file, "w") as f:
            json.dump(existing_data, f, indent=4)
    else:
        # If the file doesn't exist, save the output_data directly
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=4)


def main(video_paths):
    # Initialize data structure for JSON storage
    output_data = {
        "processed_date": datetime.now().isoformat(),
        "videos": []
    }

    # Process each video in the provided list
    for video_path in video_paths:
        print(f"Processing video: {video_path}")
        
        frames = sampler.get_frames(video_path, similarity_threshold=0.99, show=False)
        process_video(video_path, output_data, frames)

    # Save output to JSON
    save_to_json(output_data)

if __name__ == "__main__":
    # List of video paths to process
    video_paths = [
        "./input/VIRAT_S_000200_03_000657_000899.mp4",
        "./input/VIRAT_S_000200_00_000100_000171.mp4",
        "./input/VIRAT_S_000205_01_000197_000342.mp4"
    ]

    output_file="video_data_yolo.json"
    new_videos = []
    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r") as f:
            existing_data = json.load(f)

        processed_video_paths = {video["video_path"] for video in existing_data["videos"]}
        new_videos = [video for video in video_paths if video not in processed_video_paths]
    else:
        new_videos = video_paths

    main(new_videos)
