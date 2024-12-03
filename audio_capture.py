import pyaudio
import numpy as np
import logging
from flask_socketio import SocketIO

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
THRESHOLD_DB = -45  # You can adjust this value based on your testing

def get_volume(indata):
    """Convert the audio data to dB."""
    rms = np.linalg.norm(indata) / len(indata)
    if rms == 0:
        return -np.inf
    dB = 20 * np.log10(rms)
    return dB

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
