import yoloProcess as yolop
import personProcess as personp
import colorProcess as colorp
import sampleFrames as sampler
import os, json
from datetime import datetime

# --------------------------------------- YOLO Process ---------------------------------------

INPUT_DIR = './input/'

video_paths = [INPUT_DIR+f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]
print(video_paths)

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

print(f'Found {len(new_videos)} new videos to process')

# Initialize data structure for JSON storage
output_data = {
    "processed_date": datetime.now().isoformat(),
    "videos": []
}

# Process each video in the provided list
for video_path in new_videos:
    print(f"Processing video: {video_path}")
    
    print('Getting keyframes ...')
    frames = sampler.get_frames(video_path, similarity_threshold=0.99, sampling_interval=1, show=False)
    print('Detecting objects with YOLO ...')
    yolop.process_video(video_path, output_data, frames)
    print('Detecting people characteristics ...')
    personp.extract_person_segments(video_path, output_data)
    print('Identifying colors ...')
    colorp.process_videos_with_colors(output_data, ['person', 'car', 'truck', 'bus', 'boat', 'train', 'bench'])
    print(f'Done processing {video_path}')

# Save output to JSON
yolop.save_to_json(output_data)
