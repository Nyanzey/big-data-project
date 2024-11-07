import cv2
import json
import torch
from PIL import Image
from transformers import YolosFeatureExtractor, YolosForObjectDetection
from torchvision.transforms import ToTensor, ToPILImage
import matplotlib.pyplot as plt

# Load the second model and feature extractor
feature_extractor = YolosFeatureExtractor.from_pretrained('hustvl/yolos-small')
second_model = YolosForObjectDetection.from_pretrained("valentinafeve/yolos-fashionpedia")

# Categories for detected objects
cats = ['shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 'vest', 'pants', 
        'shorts', 'skirt', 'coat', 'dress', 'jumpsuit', 'cape', 'glasses', 'hat', 'headband, head covering, hair accessory', 
        'tie', 'glove', 'watch', 'belt', 'leg warmer', 'tights, stockings', 'sock', 'shoe', 'bag, wallet', 
        'scarf', 'umbrella', 'hood', 'collar', 'lapel', 'epaulette', 'sleeve', 'pocket', 'neckline', 
        'buckle', 'zipper', 'applique', 'bead', 'bow', 'flower', 'fringe', 'ribbon', 'rivet', 'ruffle', 
        'sequin', 'tassel']

def idx_to_text(i):
    return cats[i]

# Extract person segments from frames based on bounding box information
def extract_person_segments(video_path, json_path, threshold=0.5):
    with open(json_path, "r") as file:
        video_data = json.load(file)
    
    for video in video_data["videos"]:
        cap = cv2.VideoCapture(video["video_path"])
        for frame_info in video["frames"]:
            frame_number = frame_info["frame"]
            detections = frame_info["detections"]

            # Go to the correct frame in the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if not ret:
                continue
            
            for detection in detections:
                if detection["label"] == "person":
                    bbox = detection["bbox"]
                    print(bbox)
                    x1, y1, x2, y2 = map(int, bbox[0])
                    person_segment = frame[y1:y2, x1:x2]

                    # Convert to PIL image for second model processing
                    pil_img = ToPILImage()(person_segment)
                    pil_img = pil_img.resize((600, 800))
                    
                    # Apply the second model for further object identification
                    inputs = feature_extractor(images=pil_img, return_tensors="pt")
                    outputs = second_model(**inputs)

                    # Visualize predictions and extract detected labels
                    visualize_predictions(pil_img, outputs, threshold)

    cap.release()

def visualize_predictions(image, outputs, threshold=0):
    # Keep only predictions with confidence >= threshold
    probas = outputs.logits.softmax(-1)[0, :, :-1]
    keep = probas.max(-1).values > threshold

    # Convert predicted boxes from [0; 1] to image scales
    bboxes_scaled = rescale_bboxes(outputs.pred_boxes[0, keep].cpu(), image.size)
    print(bboxes_scaled)

    # Plot results
    plot_results(image, probas[keep], bboxes_scaled)

def plot_results(pil_img, prob, boxes):
    plt.figure(figsize=(16, 10))
    plt.imshow(pil_img)
    ax = plt.gca()
    colors = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125]]
    
    for p, (xmin, ymin, xmax, ymax), color in zip(prob, boxes.tolist(), colors):
        ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                   fill=False, color=color, linewidth=3))
        cl = p.argmax()
        ax.text(xmin, ymin, idx_to_text(cl), fontsize=10,
                bbox=dict(facecolor=color, alpha=0.8))
        print(idx_to_text(cl))
    plt.axis('off')
    plt.show()

# Bounding box utility functions
def box_cxcywh_to_xyxy(x):
    x_c, y_c, w, h = x.unbind(1)
    b = [(x_c - 0.5 * w), (y_c - 0.5 * h),
         (x_c + 0.5 * w), (y_c + 0.5 * h)]
    return torch.stack(b, dim=1)

def rescale_bboxes(out_bbox, size):
    img_w, img_h = size
    b = box_cxcywh_to_xyxy(out_bbox)
    b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
    return b

# Path to your JSON file and video file
video_path = "./input/VIRAT_S_000200_03_000657_000899.mp4"
json_path = "video_data_yolo.json"

# Run the segmentation extraction
extract_person_segments(video_path, json_path)
