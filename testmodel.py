import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import BatchNormalization

def test_model_loading(model_path):
    try:
        # Load the model
        model = load_model(model_path, custom_objects={'BatchNormalization': BatchNormalization})
        print("Model loaded successfully!")
        # Print model summary to verify structure
        model.summary()
    except Exception as e:
        print("Error loading model:", str(e))

# Path to your saved model
model_path = "model/128x128.h5"  # Update this to your actual model path

# Run the test
test_model_loading(model_path)
