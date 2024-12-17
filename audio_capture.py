import pyaudio
import numpy as np
import logging
import collections
import time
from model_inference import run_inference  # Import model inference module

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('audio_capture')

# Audio stream parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 2048  # Buffer size
DEVICE_INDEX = 0  # Default device (adjust as needed)

# Define the threshold for sound detection (in dB)
THRESHOLD_DB = -20  # Adjust based on testing

# Moving average window size
MOVING_AVERAGE_WINDOW = 10
rms_values = collections.deque(maxlen=MOVING_AVERAGE_WINDOW)  # Store recent RMS values

# Cooldown parameters
COOLDOWN_TIME = 2  # Cooldown period in seconds
last_detection_time = 0

def get_rms(indata):
    """
    Calculate RMS (Root Mean Square) for the given audio data.
    """
    rms = np.sqrt(np.mean(np.square(indata)))
    return rms

def moving_average(rms_value):
    """
    Smooth the RMS values using a moving average.
    """
    rms_values.append(rms_value)
    return np.mean(rms_values)

def calculate_db(rms):
    """
    Convert RMS value to decibels (dB).
    """
    return 20 * np.log10(rms) if rms > 0 else -np.inf

def start_audio_stream_process():
    """
    Capture audio, compute stable RMS, and print real-time volume updates.
    Run model inference for loud sounds with a cooldown period.
    """
    global last_detection_time
    p = pyaudio.PyAudio()

    try:
        # Open audio stream
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=DEVICE_INDEX)

        print("Audio stream started... Press Ctrl+C to stop.")

        while True:
            try:
                # Read audio data from the stream
                data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32)

                # Compute RMS and smooth it using a moving average
                rms = get_rms(data)
                smoothed_rms = moving_average(rms)

                # Convert smoothed RMS to dB
                volume_db = calculate_db(smoothed_rms)

                # Print the volume data for debugging
                print(f"Volume: {volume_db:.2f} dB")

                # Detect loud sounds exceeding the threshold with cooldown
                if volume_db > THRESHOLD_DB and (time.time() - last_detection_time > COOLDOWN_TIME):
                    print(f"LOUD SOUND DETECTED! Volume: {volume_db:.2f} dB")

                    # Run inference on detected sound
                    label, confidence = run_inference(data)
                    print(f"Prediction: {label} | Confidence: {confidence:.2f}")
                    
                    # Update the last detection time
                    last_detection_time = time.time()

            except Exception as read_error:
                print(f"Error reading audio stream: {str(read_error)}")
                break
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting audio stream.")
    finally:
        # Cleanup audio stream resources
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio stream stopped.")

if __name__ == "__main__":
    start_audio_stream_process()
