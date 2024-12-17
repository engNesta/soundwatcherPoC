from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
from audio_capture import AudioCapture  # Import the AudioCapture class
from model_inference import run_inference  # Import model inference logic

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading", logger=True, engineio_logger=True)


# Global flag to track if the thread is already running
thread_running = False
thread_lock = threading.Lock()

@app.route('/')
def index():
    """
    Serve the frontend for real-time visualization.
    """
    return render_template('index.html')

def stream_audio_data():
    """
    Background thread to capture audio and run inference.
    Emit the results to the frontend using SocketIO.
    """
    audio_capture = AudioCapture(threshold_db=-20, cooldown_time=2)
    print("Streaming audio data to connected clients...")
    try:
        while True:
            # Continuously capture audio data and calculate volume
            audio_data, volume_db = audio_capture.get_audio_data()
            if volume_db is not None:
                print(f"Emitting real-time volume: {volume_db:.2f} dB")  # Debugging log
                socketio.emit('volume_stream', {'volume': round(volume_db, 2)})


            # If a loud sound exceeds the threshold, run inference
            if audio_data is not None:
                label, confidence = run_inference(audio_data)
                socketio.emit('audio_data', {
                    'volume': round(volume_db, 2),
                    'label': label,
                    'confidence': round(confidence, 2)
                })
                print(f"Emitted Data -> Volume: {volume_db:.2f} dB | Prediction: {label} | Confidence: {confidence:.2f}%")

            time.sleep(0.1)  # Reduce CPU load
    except Exception as e:
        print(f"Error in streaming audio: {e}")
    finally:
        audio_capture.cleanup()
        print("Audio stream cleaned up.")


@socketio.on('connect')
def handle_connect():
    """
    Start streaming audio data to the client when a new connection is established.
    Ensures only one background thread runs.
    """
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
