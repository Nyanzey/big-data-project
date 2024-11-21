import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from sklearn.cluster import KMeans
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from scipy.spatial.distance import cosine

# Load model and processor globally to avoid redundant loads
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def extract_frame_features(frame):
    inputs = processor(text=[""], images=[frame], return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.image_embeds[0].cpu().numpy()  # Convert to numpy and move to CPU

def sample_video_frames(video_path, sampling_interval):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * sampling_interval)

    frame_idx = 0
    sampled_frames = []
    sampled_frame_seconds = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % interval_frames == 0:
            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            sampled_frames.append(pil_frame)
            sampled_frame_seconds[len(sampled_frames) - 1] = frame_idx
        frame_idx += 1

    cap.release()
    return sampled_frames, sampled_frame_seconds

def cluster_and_select_keyframes(frames, seconds, k_clusters, similarity_threshold):
    features = []
    for frame in frames:
        features.append(extract_frame_features(frame))
    
    features = np.array(features)  # Stack features for efficient computation
    clusters = KMeans(n_clusters=k_clusters, random_state=0).fit(features)

    keyframes = []
    for cluster_id in range(k_clusters):
        cluster_indices = np.where(clusters.labels_ == cluster_id)[0]
        representative_idx = cluster_indices[0]  # Pick the first frame initially
        keyframes.append({seconds[representative_idx]: frames[representative_idx]})
        for idx in cluster_indices[1:]:
            sim = 1 - cosine(features[representative_idx], features[idx])
            if sim < similarity_threshold:
                representative_idx = idx
                keyframes.append({seconds[representative_idx]: frames[representative_idx]})
    return keyframes

def get_frames(video_path, sampling_interval=1, similarity_threshold=0.98, k_clusters=5, show=True):
    frames, frame_seconds = sample_video_frames(video_path, sampling_interval)
    keyframes = cluster_and_select_keyframes(frames, frame_seconds, k_clusters, similarity_threshold)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    frame_indices = []
    for keyframe in keyframes:
        for frame_id, img in keyframe.items():
            frame_indices.append(frame_id)
            if show:
                print(f'Showing frame at second {frame_id / fps:.2f}')
                img.show()
                input('Press Enter to continue')

    print(f'Extracted {len(frame_indices)} keyframes from {video_path}.')
    return frame_indices