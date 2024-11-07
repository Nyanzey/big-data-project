import cv2
from sklearn.cluster import KMeans
import numpy as np
import webcolors
from collections import Counter

# Helper function to find the closest color name for a given RGB color
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
        color_name = closest_color(tuple(color_rgb))
        top_colors.append(color_name)
    
    return top_colors

# Example usage: Extract colors from a bounding box area
def analyze_object_colors(frame, bbox, top_n=3):
    x_min, y_min, x_max, y_max = bbox
    cropped_object = frame[y_min:y_max, x_min:x_max]
    colors = get_dominant_colors(cropped_object, top_n)
    label = "-".join(colors)  # Combine color names for a label
    return label

# Load a frame from a video or an image
frame = cv2.imread('./input/odorouze.png')

# Example bounding box for a detected object (e.g., a car)
bbox = (0, 0, 576, 565)  # x_min, y_min, x_max, y_max

# Analyze colors in the bounding box region and get a combined color label
label = analyze_object_colors(frame, bbox, top_n=3)

print(f"The top colors for the detected object are: {label}")
