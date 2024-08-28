import tensorflow as tf
import numpy as np
import cv2
import face_recognition
import pickle
import os

def load_models():
    try:
        model_path = "app/models/expression_model.h5"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load the emotion detection model
        emotion_model = tf.keras.models.load_model(model_path)
    except Exception as e:
        print(f"Error loading emotion model from {model_path}: {e}")
        return None, None, None

    try:
        encodings_path = "app/models/encodings.pkl"
        if not os.path.exists(encodings_path):
            raise FileNotFoundError(f"Encodings file not found: {encodings_path}")
        
        # Load known face encodings and names from a pickle file
        with open(encodings_path, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, tuple) and len(data) == 2:
                known_face_encodings, known_face_names = data
            else:
                raise ValueError(f"Encodings file does not contain the expected data format: {encodings_path}")
    except Exception as e:
        print(f"Error loading encodings from {encodings_path}: {e}")
        return emotion_model, None, None

    return emotion_model, known_face_encodings, known_face_names

def preprocess_image(image):
    try:
        # Convert to Grayscale (if your model expects grayscale images)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize (match the input size of your model)
        target_size = (64, 64)  # Ensure this matches the input size expected by your model
        resized_image = cv2.resize(gray_image, target_size)
        
        # Normalize (scale pixel values to 0-1 range)
        normalized_image = resized_image / 255.0
        
        # Expand dimensions to match the expected input shape for the model
        expanded_image = np.expand_dims(normalized_image, axis=0) 
        expanded_image = np.expand_dims(expanded_image, axis=-1)
        
        return expanded_image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None
