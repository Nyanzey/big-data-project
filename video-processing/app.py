from flask import Flask, request, jsonify
import requests
import boto3
import os
import tempfile
from detection.detect import get_detections

app = Flask(__name__)

# Set the URL of the other container (destination)
index_host = os.getenv("INDEX_SERVICE_HOST", "inverted-index-service")
index_port = os.getenv("INDEX_SERVICE_PORT", "5002")
DESTINATION_URL = f"http://{index_host}:{index_port}/receive_metadata"

# Get settings from environment variables
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv("AWS_ACCESS_KEY_ID", "")
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "surv-cloud-videos")

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def download_from_s3(video_key):
    """Download videos from S3 and return list of local file paths."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    s3_client.download_fileobj(AWS_S3_BUCKET, video_key, temp_file)
    temp_file.close()
    return temp_file.name

@app.route('/process-videos', methods=['POST'])
def process_videos():
    data = request.get_json()
    if not data or 'fileName' not in data:
        return jsonify({'error': 'Missing file name'}), 400

    video_key = data['fileName']  # These are S3 object keys
    if not isinstance(video_key, str):
        return jsonify({'error': 'file name must be a string'}), 400

    try:
        # Download videos from S3
        local_video_path = download_from_s3(video_key)
        print("Downloaded video files:", local_video_path)

        # Call your detection function
        print("local_video_path:", local_video_path)
        metadata = get_detections([local_video_path]) # Replace with actual detection function call
        #print("Metadata:", metadata)

        # Send the metadata to the destination container
        response = requests.post(DESTINATION_URL, json=metadata)
        response.raise_for_status()

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            os.unlink(local_video_path)
        except Exception as e:
            print(f"Failed to delete temp file {local_video_path}: {e}")
    return jsonify({'status': 'success'}), 200
