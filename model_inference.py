import numpy as np
import tensorflow.lite as tflite
from scipy.signal import resample
import librosa

# Load the TFLite model
MODEL_PATH = "model/Low Cost Gunshot Detection Model.tflite"
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Function to preprocess audio for model input
def preprocess_audio(audio_data):
    """
    Preprocess audio data to generate a 2D spectrogram and match the TFLite model input shape.
    """
    # Normalize audio data
    audio_data = np.array(audio_data, dtype=np.float32) / 32768.0  # Scale to [-1, 1]

    # Resample or trim to match expected input length (e.g., 128 samples)
    target_length = 16000  # Resample to 16kHz if needed
    audio_data = resample(audio_data, target_length)

    # Generate a Mel-spectrogram with 128 frequency bins and 128 time frames
    mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=16000, n_mels=128, hop_length=128)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)  # Convert to decibel scale

    # Ensure the spectrogram has the shape (128, 128)
    if mel_spectrogram.shape[1] < 128:
        mel_spectrogram = np.pad(mel_spectrogram, ((0, 0), (0, 128 - mel_spectrogram.shape[1])), mode='constant')
    elif mel_spectrogram.shape[1] > 128:
        mel_spectrogram = mel_spectrogram[:, :128]
    mel_spectrogram = mel_spectrogram[:128, :128]

    # Reshape to fit model input shape (1, 128, 128, 1)
    model_input = np.expand_dims(mel_spectrogram, axis=0)  # Add batch dimension
    model_input = np.expand_dims(model_input, axis=-1)  # Add channel dimension

    return model_input

# Function to run inference on preprocessed audio
def run_inference(audio_data):
    """
    Run inference on the preprocessed audio data.
    """
    # Preprocess the audio data
    model_input = preprocess_audio(audio_data)

    # Debugging: Print input shape
    print(f"Model input shape: {input_details[0]['shape']}")
    print(f"Provided input shape: {model_input.shape}")

    # Set input tensor and invoke interpreter
    interpreter.set_tensor(input_details[0]['index'], model_input)
    interpreter.invoke()

    # Get output tensor and interpret results
    output_data = interpreter.get_tensor(output_details[0]['index'])
    class_labels = ["Other", "Gunshot"]
    predicted_class_index = np.argmax(output_data)
    predicted_class_label = class_labels[predicted_class_index]
    confidence = output_data[0][predicted_class_index] * 100  # Confidence as percentage

    # Output the result
    result_text = f"Model: {MODEL_PATH}\nPredicted class: {predicted_class_label}\nConfidence: {confidence:.2f}%\n"
    print(result_text)

    return predicted_class_label, confidence

if __name__ == "__main__":
    # Example usage:
    test_audio_data = np.zeros(16000, dtype=np.int16)  # Placeholder for testing
    label, confidence = run_inference(test_audio_data)
    print(f"Prediction: {label} | Confidence: {confidence:.2f}%")
