import cv2  # OpenCV for webcam access
import base64
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time
import json
from datetime import datetime
from audio_capture import AudioCapture
from model_inference import run_inference

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Global variables
logs = []
LOG_FILE = "logs.json"
thread_running = False
webcam_running = False
thread_lock = threading.Lock()

@app.route('/')
def index():
    """Serve the frontend for real-time visualization."""
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    """Serve the full logs as JSON."""
    try:
        with open(LOG_FILE, 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([])

def log_event(event):
    """Append an event to logs and save to a JSON file."""
    global logs
    logs.append(event)
    if len(logs) > 50:
        logs.pop(0)

    with open(LOG_FILE, 'w') as file:
        json.dump(logs, file, indent=4)

    socketio.emit('log_event', event)

def stream_audio_data():
    """Background thread to capture audio, run inference, and log events."""
    audio_capture = AudioCapture(threshold_db=-20, cooldown_time=2)
    print("Streaming audio data to connected clients...")
    try:
        while True:
            audio_data, volume_db = audio_capture.get_audio_data()
            if volume_db is not None:
                socketio.emit('volume_stream', {'volume': round(volume_db, 2)})

                if audio_data is not None:
                    label, confidence = run_inference(audio_data)
                    event = {
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'volume': round(volume_db, 2),
                        'prediction': label,
                        'confidence': round(confidence, 2)
                    }
                    log_event(event)
            time.sleep(0.1)
    finally:
        audio_capture.cleanup()

def stream_webcam():
    """Background thread to capture and stream webcam frames."""
    global webcam_running
    webcam_running = True
    video_capture = cv2.VideoCapture(0)  # Open webcam (default: 0)
    try:
        while webcam_running:
            ret, frame = video_capture.read()
            if not ret:
                continue

            # Encode the frame to JPEG and convert to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Emit the frame to the frontend
            socketio.emit('webcam_frame', {'frame': frame_base64})
            time.sleep(0.05)  # Stream at ~20 FPS
    except Exception as e:
        print(f"Error in webcam stream: {e}")
    finally:
        video_capture.release()
        print("Webcam stream stopped.")

@socketio.on('connect')
def handle_connect():
    """Start threads when a new client connects."""
    global thread_running, webcam_running
    with thread_lock:
        if not thread_running:
            print("Client connected. Starting audio streaming...")
            thread_running = True
            threading.Thread(target=stream_audio_data, daemon=True).start()

        if not webcam_running:
            print("Starting webcam streaming...")
            threading.Thread(target=stream_webcam, daemon=True).start()

if __name__ == "__main__":
    print("Starting Flask server...")
    socketio.run(app, debug=True)
