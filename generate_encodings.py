import face_recognition
import pickle
import os
from pathlib import Path

# Define the directory paths within the Docker container
KNOWN_FACES_DIR = "app/known_faces"  # Change this to wherever your known faces are stored
OUTPUT_PATH = "app/models/encodings.pkl"

# Ensure the models directory exists
MODELS_DIR = Path("app/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def generate_encodings(known_faces=KNOWN_FACES_DIR, output_path=OUTPUT_PATH):
    known_face_encodings = []
    known_face_names = []

    # Loop through each image in the known faces directory
    for filename in os.listdir(known_faces):
        if filename.endswith((".jpeg", ".png", ".jpg")):  # Include .jpg extension
            # Load the image
            image_path = os.path.join(known_faces, filename)
            image = face_recognition.load_image_file(image_path)

            # Get face encodings for the face(s) in the image
            encodings = face_recognition.face_encodings(image)
            if encodings:
                # Use the first encoding found in the image (assuming one face per image)
                known_face_encodings.append(encodings[0])
                # Use the filename (without extension) as the name
                known_face_names.append(os.path.splitext(filename)[0])

    # Save the face encodings and names to a pickle file
    with open(output_path, "wb") as f:
        pickle.dump((known_face_encodings, known_face_names), f)

    print(f"Encodings and names saved to {output_path}")
