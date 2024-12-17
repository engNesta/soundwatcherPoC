import base64
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
from audio_capture import AudioCapture  # Import the AudioCapture class
from model_inference import run_inference  # Import model inference logic

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Global flags
thread_running = False
thread_lock = threading.Lock()
webcam_active = False  # Flag for webcam streaming

def stream_webcam(duration=10):
    """
    Stream webcam frames for a limited duration when triggered.
    """
    global webcam_active
    if webcam_active:
        return  # Avoid starting multiple streams

    webcam_active = True
    cap = cv2.VideoCapture(0)  # Open the webcam
    start_time = time.time()

    print("Webcam streaming started...")
    try:
        while time.time() - start_time < duration:  # Stream for the specified duration
            ret, frame = cap.read()
            if ret:
                # Encode the frame as a base64 string
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                socketio.emit('webcam_frame', {'frame': frame_base64})
            time.sleep(0.05)  # Adjust frame rate
    finally:
        cap.release()
        webcam_active = False
        print("Webcam streaming stopped.")


def stream_audio_data():
    """
    Background thread to capture audio and run inference.
    Emit the results to the frontend using SocketIO.
    """
    audio_capture = AudioCapture(threshold_db=-20, cooldown_time=2)
    print("Streaming audio data to connected clients...")
    try:
        while True:
            audio_data, volume_db = audio_capture.get_audio_data()

            if volume_db is not None:
                # Emit real-time volume data
                socketio.emit('volume_stream', {'volume': round(volume_db, 2)})

            if audio_data is not None:
                # Run inference
                label, confidence = run_inference(audio_data)
                socketio.emit('audio_data', {
                    'volume': round(volume_db, 2),
                    'label': label,
                    'confidence': round(confidence, 2)
                })

                print(f"Emitted Data -> Volume: {volume_db:.2f} dB | Prediction: {label} | Confidence: {confidence:.2f}%")

                # Activate webcam stream when the threshold is crossed
                threading.Thread(target=stream_webcam, args=(10,), daemon=True).start()

            time.sleep(0.1)  # Reduce CPU load
    finally:
        audio_capture.cleanup()


@app.route('/')
def index():
    """
    Serve the frontend for real-time visualization.
    """
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """
    Start streaming audio data when the client connects.
    """
    global thread_running
    with thread_lock:
        if not thread_running:
            print("Client connected. Starting audio streaming...")
            thread_running = True
            threading.Thread(target=stream_audio_data, daemon=True).start()
        else:
            print("Client connected. Streaming already running.")


if __name__ == "__main__":
    print("Starting Flask server...")
    socketio.run(app, debug=True)
