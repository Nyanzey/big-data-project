import cv2
import json
import torch
from PIL import Image
from transformers import YolosFeatureExtractor, YolosForObjectDetection
from torchvision.transforms import ToPILImage
import matplotlib.pyplot as plt

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# Load the second model and feature extractor
feature_extractor = YolosFeatureExtractor.from_pretrained('hustvl/yolos-small')
second_model = YolosForObjectDetection.from_pretrained("valentinafeve/yolos-fashionpedia").to(device)

# Categories for detected objects
cats = [
    'shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 'vest', 'pants',
    'shorts', 'skirt', 'coat', 'dress', 'jumpsuit', 'cape', 'glasses', 'hat', 'headband, head covering, hair accessory',
    'tie', 'glove', 'watch', 'belt', 'leg warmer', 'tights, stockings', 'sock', 'shoe', 'bag, wallet',
    'scarf', 'umbrella', 'hood', 'collar', 'lapel', 'epaulette', 'sleeve', 'pocket', 'neckline',
    'buckle', 'zipper', 'applique', 'bead', 'bow', 'flower', 'fringe', 'ribbon', 'rivet', 'ruffle',
    'sequin', 'tassel'
]

def idx_to_text(i):
    return cats[i]

def extract_person_segments(video_path, video_data, threshold=0.5, default_clothes=['shirt', 'pants']):
    """Process video frames to detect people and identify their clothes."""
    cap = None
    for video in video_data["videos"]:
        if video["video_path"] == video_path:
            cap = cv2.VideoCapture(video_path)
            for frame_info in video["frames"]:
                frame_number = frame_info["frame"]
                detections = frame_info["detections"]

                # Process each frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()
                if not ret:
                    continue

                for detection in detections:
                    if detection["label"] == "person":
                        bbox = detection["bbox"]
                        x1, y1, x2, y2 = map(int, bbox[0])
                        person_segment = frame[y1:y2, x1:x2]

                        # Convert to PIL image and resize for second model processing
                        pil_img = Image.fromarray(person_segment)
                        pil_img = pil_img.resize((600, 800))

                        # Object detection on the cropped person segment
                        inputs = feature_extractor(images=pil_img, return_tensors="pt").to(device)
                        outputs = second_model(**inputs)

                        # Get detected clothes
                        clothes = visualize_predictions(pil_img, outputs, threshold, show=False)
                        detection['clothes'] = default_clothes + clothes if clothes else default_clothes

            break

    if cap:
        print(f"Processed people in {video_path}")
        cap.release()
    else:
        print(f"Video path not found: {video_path}")

    return video_data

def visualize_predictions(image, outputs, threshold=0.5, show=False):
    """Visualize predictions and extract labels above the threshold."""
    probas = outputs.logits.softmax(-1)[0, :, :-1]
    keep = probas.max(-1).values > threshold

    if keep.sum() == 0:
        return []

    bboxes_scaled = rescale_bboxes(outputs.pred_boxes[0, keep].cpu(), image.size)
    return plot_results(image, probas[keep], bboxes_scaled, show)

def plot_results(pil_img, prob, boxes, show=False):
    """Plot results and return detected classes."""
    if not boxes.size(0):
        return []

    result = []
    plt.figure(figsize=(16, 10))
    plt.imshow(pil_img)
    ax = plt.gca()
    colors = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125]]

    for p, (xmin, ymin, xmax, ymax), color in zip(prob, boxes.tolist(), colors):
        cl = p.argmax()
        result.append(idx_to_text(cl))
        ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, fill=False, color=color, linewidth=3))
        ax.text(xmin, ymin, idx_to_text(cl), fontsize=10, bbox=dict(facecolor=color, alpha=0.8))

    plt.axis('off')
    if show:
        plt.show()

    return result

def box_cxcywh_to_xyxy(x):
    """Convert box format from center to corner coordinates."""
    x_c, y_c, w, h = x.unbind(1)
    b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
    return torch.stack(b, dim=1)

def rescale_bboxes(out_bbox, size):
    """Rescale bounding boxes to image size."""
    img_w, img_h = size
    b = box_cxcywh_to_xyxy(out_bbox)
    b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
    return b