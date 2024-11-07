import cv2
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sklearn.cluster import KMeans
from scipy.spatial.distance import cosine
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def extract_frame_features(frame):
    inputs = processor(text=[""], images=[frame], return_tensors="pt", padding=True)

    outputs = model(**inputs)
    embedding = outputs.image_embeds[0]
    return embedding

def sample_video_frames(video_path, sampling_interval):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * sampling_interval)
    sampled_frames = []
    sampled_frames_seconds = {}
    
    frame_idx = 0
    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % interval_frames == 0:
            # Convert the frame from BGR (OpenCV format) to RGB (PIL format)
            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            sampled_frames.append(pil_frame)
            sampled_frames_seconds[i] = frame_idx
            i += 1
        frame_idx += 1

    cap.release()
    return sampled_frames, sampled_frames_seconds

def cluster_and_select_keyframes(frames, seconds, k_clusters, similarity_threshold):
    features = [extract_frame_features(frame) for frame in frames]
    clusters = KMeans(n_clusters=k_clusters).fit([feature.detach().numpy() for feature in features])

    keyframes = []
    for cluster_id in range(k_clusters):
        cluster_indices = np.where(clusters.labels_ == cluster_id)[0]
        cluster_features = [features[i] for i in cluster_indices]
        
        # Select a representative frame with minimal overlap
        representative_idx = cluster_indices[0]  # Start with the first frame in the cluster
        keyframes.append({seconds[representative_idx]:frames[representative_idx]})
        
        for idx in cluster_indices[1:]:
            sim = torch.nn.functional.cosine_similarity(cluster_features[0], features[idx], dim=0).item()
            if sim < similarity_threshold:
                representative_idx = idx
                keyframes.append({seconds[representative_idx]:frames[representative_idx]})

    return keyframes

def get_frames(video_path, sampling_interval=1, similarity_threshold=0.98, k_clusters=5, show=True):
    frames, frame_seconds = sample_video_frames(video_path, sampling_interval)
    keyframes = cluster_and_select_keyframes(frames, frame_seconds, k_clusters, similarity_threshold)
    frame_indices = []

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Save or display keyframes
    for idx, frame in enumerate(keyframes):
        for frame_id, img in frame.items():
            frame_indices.append(frame_id)
            if show:
                print(f'Showing frame at second {frame_id/fps}')
                img.show()
                input('Press enter to continue')

    print(f'Extracted {len(frame_indices)} keyframes from {video_path}.')
    return frame_indices
