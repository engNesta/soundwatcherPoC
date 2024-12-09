import pyaudio
import numpy as np
import logging
from flask_socketio import SocketIO
import collections

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('audio_capture')

# Set parameters for audio capture
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 2048  # Increased buffer size
DEVICE_INDEX = 0  # Default device

# Define the threshold for gunshots (in dB)
THRESHOLD_DB = -60  # You can adjust this value based on your testing

# Create a deque to store the last RMS values for moving average
MOVING_AVERAGE_WINDOW = 10  # Number of RMS values to average
rms_values = collections.deque(maxlen=MOVING_AVERAGE_WINDOW)

def get_rms(indata):
    """Calculate RMS (Root Mean Square) of the incoming audio data."""
    rms = np.linalg.norm(indata) / len(indata)
    if rms == 0:
        return 0
    return rms

def moving_average(rms_value):
    """Apply moving average to smooth out the RMS values."""
    rms_values.append(rms_value)
    return np.mean(rms_values)

def get_volume(indata):
    """Get the RMS value and smooth it using moving average, then convert to dB."""
    rms = get_rms(indata)
    smoothed_rms = moving_average(rms)
    # Convert to dB
    if smoothed_rms == 0:
        return -np.inf  # No sound
    return 20 * np.log10(smoothed_rms)

def start_audio_stream_process(socketio):
    """Function to start audio capture and emit volume updates."""
    p = pyaudio.PyAudio()
    
    # Start the audio stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=DEVICE_INDEX)

    logger.info("Audio stream started...")

    try:
        while True:
            data = np.frombuffer(stream.read(CHUNK), dtype=np.float32)
            volume = get_volume(data)
            
            # Check if the volume exceeds the threshold and trigger an action
            if volume > THRESHOLD_DB:
                logger.info(f"Gunshot or loud sound detected! Volume: {volume:.2f} dB")
            
            # Emit the volume data to the WebSocket
            socketio.emit('volume_update', {'volume': float(volume)})

            # Log volume for debugging
            logger.debug(f"Volume: {volume:.2f} dB")
    except Exception as e:
        logger.error(f"Error starting the audio stream: {str(e)}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        logger.info("Audio stream stopped.")
