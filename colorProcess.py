import cv2
from sklearn.cluster import KMeans
import numpy as np
import webcolors
from collections import Counter
import json
import matplotlib.pyplot as plt

COMMON_COLORS = {
    "red": [
        (255, 0, 0),         # Red
        (255, 102, 102),     # Light Red
        (139, 0, 0),         # Dark Red
        (178, 34, 34),       # Firebrick
        (220, 20, 60),       # Crimson
    ],
    "green": [
        (0, 128, 0),         # Green
        (144, 238, 144),     # Light Green
        (0, 100, 0),         # Dark Green
        (34, 139, 34),       # Forest Green
        (0, 255, 0),         # Lime
    ],
    "blue": [
        (0, 0, 255),         # Blue
        (173, 216, 230),     # Light Blue
        (0, 0, 139),         # Dark Blue
        (135, 206, 235),     # Sky Blue
        (0, 0, 128),         # Navy
    ],
    "yellow": [
        (255, 255, 0),       # Yellow
        (255, 255, 224),     # Light Yellow
        (204, 204, 0),       # Dark Yellow
    ],
    "orange": [
        (255, 165, 0),       # Orange
        (255, 204, 153),     # Light Orange
        (255, 140, 0),       # Dark Orange
    ],
    "purple": [
        (128, 0, 128),       # Purple
        (230, 230, 250),     # Lavender
        (238, 130, 238),     # Violet
        (75, 0, 130),        # Dark Purple
    ],
    "pink": [
        (255, 192, 203),     # Pink
        (255, 182, 193),     # Light Pink
        (255, 105, 180),     # Dark Pink
    ],
    "gray": [
        (128, 128, 128),     # Gray
        (211, 211, 211),     # Light Gray
        (169, 169, 169),     # Dark Gray
    ],
    "cyan": [
        (0, 255, 255),       # Cyan
        (224, 255, 255),     # Light Cyan
        (0, 139, 139),       # Dark Cyan
    ],
    "magenta": [
        (255, 0, 255),       # Magenta
        (255, 182, 193),     # Light Magenta
    ],
    "black": [
        (0, 0, 0),           # Black
    ],
    "white": [
        (255, 255, 255),     # White
    ],
}

def simple_closest_color(requested_color):
    min_distance = float('inf')
    closest_name = None
    
    # Compare the requested color with each color group in COMMON_COLORS
    for color_name, color_shades in COMMON_COLORS.items():
        for color_rgb in color_shades:
            distance = np.sqrt(np.sum((np.array(color_rgb) - np.array(requested_color)) ** 2))
            
            if distance < min_distance:
                min_distance = distance
                closest_name = color_name
    
    return closest_name

# Using webcolors name library
def closest_color(requested_colour):
    min_colours = {}
    for name in webcolors.names("css3"):
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_dominant_colors(image, top_n_colors=3):
    # Reshape the image for clustering
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=top_n_colors)
    kmeans.fit(image)
    
    # Count dominant colors
    counts = Counter(kmeans.labels_)
    centers = kmeans.cluster_centers_

    # Map dominant colors to color names
    top_colors = []
    for idx in counts.most_common(top_n_colors):
        color_rgb = centers[idx[0]].astype(int)
        color_name = simple_closest_color(tuple(color_rgb))
        top_colors.append(color_name)

    # Visualize clusters
    """
    plt.figure(figsize=(8, 4))
    for i, (count, center) in enumerate(counts.most_common(top_n_colors)):
        color_patch = np.zeros((50, 50, 3), dtype=int)
        color_patch[:, :] = centers[count].astype(int)
        plt.subplot(1, top_n_colors, i + 1)
        plt.imshow(color_patch.astype(int))
        plt.title(f"{top_colors[i]}")
        plt.axis("off")
    plt.show()
    """
    
    return top_colors

def analyze_colors_in_bboxes(video_path, frame_num, bbox, top_n=3):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()

    if not ret:
        print(f"Error: Could not read frame {frame_num} from {video_path}")
        cap.release()
        return []

    x_min, y_min, x_max, y_max = map(int, bbox)
    cropped_object = frame[y_min:y_max, x_min:x_max]
    #plt.imshow(cv2.cvtColor(cropped_object, cv2.COLOR_BGR2RGB))
    #plt.title(f"Cropped Segment for Frame {frame_num}")
    #plt.axis('off')
    #plt.show()
    colors = get_dominant_colors(cropped_object, top_n)
    cap.release()
    return colors

def process_videos_with_colors(data, object_labels, top_n_colors=3):
    for video in data["videos"]:
        video_path = video["video_path"]
        for frame_info in video["frames"]:
            frame_num = frame_info["frame"]
            for detection in frame_info["detections"]:
                if detection["label"] in object_labels:
                    bbox = detection["bbox"][0]
                    colors = analyze_colors_in_bboxes(video_path, frame_num, bbox, top_n=top_n_colors)
                    detection["colors"] = colors

"""
# Sample usage
object_labels_to_process = ["person"]

with open("video_data_yolo.json") as f:
    data = json.load(f)

processed_data = process_videos_with_colors(data, object_labels_to_process, top_n_colors=5)

# Save the updated JSON structure to a file
with open("final_detection_data.json", "w") as f:
    json.dump(processed_data, f, indent=4)

"""