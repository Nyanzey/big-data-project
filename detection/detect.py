import detection.yoloProcess as yolop
import detection.colorProcess as colorp
import detection.sampleFrames as sampler
import os, json
from datetime import datetime

# --------------------------------------- YOLO Process ---------------------------------------

# Input: list of video paths to process
def get_detections(video_paths):
    output_file="video_data_test.json"

    new_videos = []
    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r") as f:
            existing_data = json.load(f)
        processed_video_paths = {video["video_path"] for video in existing_data["videos"]}
        new_videos = [video for video in video_paths if video not in processed_video_paths]
    else:
        new_videos = video_paths

    # Initialize data structure for JSON storage
    output_data = {
        "processed_date": datetime.now().isoformat(),
        "videos": []
    }

    # Process each video in the provided list
    for video_path in new_videos:
        frames = sampler.get_frames(video_path, similarity_threshold=0.99, sampling_interval=1, show=False)
        yolop.process_video(video_path, output_data, frames)
        colorp.process_videos_with_colors(output_data, ['person', 'car', 'truck', 'bus', 'boat', 'train', 'bench'])
        
    # Save output to JSON
    return output_data
