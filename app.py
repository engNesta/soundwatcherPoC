from flask import Flask
import logging
from audio_capture import start_audio_stream_process  # Import the audio capture function

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app")

app = Flask(__name__)

@app.route('/')
def index():
    return "Audio stream is running... Check the console for real-time volume updates."

if __name__ == "__main__":
    try:
        # Start audio stream in the background
        logger.info("Starting audio stream...")
        start_audio_stream_process()
    except Exception as e:
        logger.error(f"Error starting audio stream: {e}")
