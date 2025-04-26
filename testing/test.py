# Example test script to send a request to the Flask API

import requests

# URL of your Flask API
API_URL = "http://127.0.0.1:5000/process_videos"

# Example payload with a list of video paths
payload = {
    "video_paths": [
        "videos/test.mp4"
    ]
}

def send_test_request():
    try:
        response = requests.post(API_URL, json=payload)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        print("Request failed:", e)

if __name__ == "__main__":
    send_test_request()