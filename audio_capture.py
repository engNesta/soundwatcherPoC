import pyaudio
import numpy as np
import logging
import collections
import time
from model_inference import run_inference  # Import model inference module


class AudioCapture:
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 2048  # Buffer size
    DEVICE_INDEX = 0  # Default device (adjust as needed)

    def __init__(self, threshold_db=-20, cooldown_time=2):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.threshold_db = threshold_db
        self.cooldown_time = cooldown_time
        self.last_detection_time = 0
        self.rms_values = collections.deque(maxlen=10)

    def get_rms(self, indata):
        return np.sqrt(np.mean(np.square(indata)))

    def moving_average(self, rms_value):
        self.rms_values.append(rms_value)
        return np.mean(self.rms_values)

    def calculate_db(self, rms):
        return 20 * np.log10(rms) if rms > 0 else -np.inf

    def get_audio_data(self):
        try:
            if self.stream is None:
                self.stream = self.p.open(format=self.FORMAT,
                                          channels=self.CHANNELS,
                                          rate=self.RATE,
                                          input=True,
                                          frames_per_buffer=self.CHUNK,
                                          input_device_index=self.DEVICE_INDEX)
            data = np.frombuffer(self.stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.float32)
            rms = self.get_rms(data)
            smoothed_rms = self.moving_average(rms)
            volume_db = self.calculate_db(smoothed_rms)
    
            # Always return the volume_db for real-time display
            if volume_db > self.threshold_db and (time.time() - self.last_detection_time > self.cooldown_time):
                self.last_detection_time = time.time()
                return data, volume_db  # Return data and volume when threshold is exceeded
    
            # If threshold is not exceeded, return None for data but still return volume
            return None, volume_db
    
        except Exception as e:
            print(f"Error capturing audio data: {e}")
            return None, None



    def cleanup(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()


def start_audio_stream_process():
    audio_capture = AudioCapture()
    print("Audio stream started... Press Ctrl+C to stop.")
    try:
        while True:
            audio_data, volume_db = audio_capture.get_audio_data()
            if audio_data is not None:
                print(f"LOUD SOUND DETECTED! Volume: {volume_db:.2f} dB")
                label, confidence = run_inference(audio_data)
                print(f"Prediction: {label} | Confidence: {confidence:.2f}%")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting audio stream.")
    except Exception as e:
        logging.error(f"Error during audio stream process: {e}")
    finally:
        audio_capture.cleanup()
        print("Audio stream stopped.")


if __name__ == "__main__":
    start_audio_stream_process()
