from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Internal service URLs (use Kubernetes service names)
PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://processor-service:5000")

@app.route("/process-videos", methods=["POST"])
def process_videos():
    data = request.get_json()
    try:
        res = requests.post(f"{PROCESSOR_URL}/process-videos", json=data)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    return "Flask Router is running", 200
