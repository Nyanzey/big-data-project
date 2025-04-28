from flask import Flask, request, jsonify
import requests
import boto3
import os
import tempfile
from detection.detect import get_detections

app = Flask(__name__)

# Set the URL of the other container (destination)
DESTINATION_URL = "http://metadata-service:5000/"

# Get settings from environment variables
os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "surv-cloud-videos")

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def download_from_s3(video_keys):
    """Download videos from S3 and return list of local file paths."""
    local_paths = []
    for key in video_keys:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        s3_client.download_fileobj(AWS_S3_BUCKET, key, temp_file)
        temp_file.close()
        local_paths.append(temp_file.name)
    return local_paths

@app.route('/process_videos', methods=['POST'])
def process_videos():
    data = request.get_json()
    if not data or 'video_paths' not in data:
        return jsonify({'error': 'Missing video_paths'}), 400

    video_keys = data['video_paths']  # These are S3 object keys
    if not isinstance(video_keys, list):
        return jsonify({'error': 'video_paths must be a list'}), 400

    try:
        # Download videos from S3
        local_video_paths = download_from_s3(video_keys)

        # Call your detection function
        metadata = get_detections(local_video_paths)
        print("Metadata:", metadata)

        # Send the metadata to the destination container
        response = requests.post(DESTINATION_URL, json=metadata)
        response.raise_for_status()

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up downloaded temporary files
        for path in local_video_paths:
            try:
                os.unlink(path)
            except Exception as e:
                print(f"Failed to delete temp file {path}: {e}")

    return jsonify({'status': 'success', 'metadata_sent': metadata}), 200

# Health check (optional)
@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)