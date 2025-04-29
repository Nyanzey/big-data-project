# Example receiver script to receive metadata from the Flask API

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_metadata', methods=['POST'])
def receive_metadata():
    data = request.get_json()
    print("Received metadata:", data)
    return jsonify({'status': 'metadata received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)