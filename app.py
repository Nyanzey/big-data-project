# API for processing videos and sending metadata to another container

from flask import Flask, request, jsonify
import requests
from detection.detect import get_detections

app = Flask(__name__)

# Set the URL of the other container (destination)
DESTINATION_URL = "http://localhost:5001/receive_metadata"

@app.route('/process_videos', methods=['POST'])
def process_video():
    data = request.get_json()
    if not data or 'video_paths' not in data:
        return jsonify({'error': 'Missing video_paths'}), 400

    video_paths = data['video_paths']
    if not isinstance(video_paths, list):
        return jsonify({'error': 'video_paths must be a list'}), 400

    # Call your detection function (already implemented)
    metadata = get_detections(video_paths)
    print("Metadata:", metadata)

    # Send the metadata to the destination container
    try:
        response = requests.post(DESTINATION_URL, json=metadata)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'status': 'success', 'metadata_sent': metadata}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)