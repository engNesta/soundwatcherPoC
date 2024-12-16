import tensorflow as tf
import numpy as np

def load_tflite_model(model_path):
    try:
        # Load the TFLite model
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        # Get model input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Print input and output details for debugging
        print("Model loaded successfully!")
        print(f"Input Details: {input_details}")
        print(f"Output Details: {output_details}")
        
        return interpreter
    except Exception as e:
        print(f"Error loading TFLite model: {e}")
        return None

# Path to your TFLite model
model_path = "model/Low Cost Gunshot Detection Model.tflite"

# Test the model loading
interpreter = load_tflite_model(model_path)

# Additional test: Check if the model can handle dummy input
if interpreter:
    # Create dummy input data based on the model's input shape
    input_details = interpreter.get_input_details()
    input_shape = input_details[0]['shape']  # Get input shape
    dummy_input = np.random.random_sample(input_shape).astype(np.float32)  # Create random data

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], dummy_input)
    interpreter.invoke()

    # Get the output data
    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    print("Inference successful!")
    print(f"Output Data: {output_data}")
