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
logs = []  # In-memory log storage
LOG_FILE = "logs.json"  # JSON file to store logs
thread_running = False
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
    """
    Append an event to the logs and save to a JSON file.
    Event format: {'time': ..., 'volume': ..., 'prediction': ..., 'confidence': ...}
    """
    global logs
    logs.append(event)
    if len(logs) > 50:  # Keep the log size manageable
        logs.pop(0)

    # Save to JSON file
    with open(LOG_FILE, 'w') as file:
        json.dump(logs, file, indent=4)

    # Emit the log to the frontend
    socketio.emit('log_event', event)

def stream_audio_data():
    """Background thread to capture audio, run inference, and log events."""
    audio_capture = AudioCapture(threshold_db=-20, cooldown_time=2)
    print("Streaming audio data to connected clients...")
    try:
        while True:
            audio_data, volume_db = audio_capture.get_audio_data()
            if volume_db is not None:
                # Emit real-time volume
                socketio.emit('volume_stream', {'volume': round(volume_db, 2)})
                print(f"Volume: {volume_db:.2f} dB")

                # Log event when volume is above threshold
                if audio_data is not None:
                    label, confidence = run_inference(audio_data)
                    event = {
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'volume': round(volume_db, 2),
                        'prediction': label,
                        'confidence': round(confidence, 2)
                    }
                    log_event(event)
                    print(f"Logged Event -> {event}")
            time.sleep(0.1)
    except Exception as e:
        print(f"Error in streaming audio: {e}")
    finally:
        audio_capture.cleanup()
        print("Audio stream cleaned up.")

@socketio.on('connect')
def handle_connect():
    """Start streaming audio data when a new connection is established."""
    global thread_running
    with thread_lock:
        if not thread_running:
            print("Client connected. Starting audio streaming...")
            thread_running = True
            threading.Thread(target=stream_audio_data, daemon=True).start()
        else:
            print("Client connected. Audio streaming already running.")

if __name__ == "__main__":
    print("Starting Flask server...")
    socketio.run(app, debug=True)
