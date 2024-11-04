from ultralytics import YOLO

# Load a model
model = YOLO("models/yolo11x.pt")

# Perform object detection on an image
results = model("input/PC_22.jpg")
results[0].show()
