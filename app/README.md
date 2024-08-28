The app turns your webcam into a smart tool that can tell how students are feeling. When the camera is on, it recognizes each student's face and tries to figure out their current emotion. The app then shares this information so teachers or others can see how everyone is doing. It's like having a helper who can quickly read the room and give clues about the mood of the class.

**How it Works:**

1. **FastAPI Back-end:**
    
    - A FastAPI server is running at `http://127.0.0.1:8000/recognize`.
    - It expects video data (likely JPEG-encoded) as input.
    - It processes the video, performing face recognition and emotion detection.
    - It returns a JSON response with the recognized name and detected emotion.
2. **OpenCV Front-end:**
    
    - It captures frames from the default webcam.
    - It encodes each frame as JPEG.
    - It sends the encoded frame to the FastAPI back-end for processing.
    - It receives the JSON response and prints the recognized name and emotion to the console.
    - It displays the webcam frame with a title 'Webcam' in a qwindow.
    - It continues this loop until the user presses the 'q' key.
### Technical Implementation
1. Create a python virtual environment using the following command:
		`python3 -m venv emotion_and_recognition`
2. Activate the environment:
		`source emotion_and_recognition/bin/activate`
3. Install all the dependencies in the file `requirements.txt`
		`pip install -r requirements.txt`
4. The `requirements.txt` file contains following libraries:
```
opencv-python
dlib
tensorflow
numpy
scikit-learn
fastapi
```
5. Run the script for FastAPI back-end and also run `client.py` in another terminal.
```
uvicorn app.main:app --reload
```

In another terminal run:
```
python client.py
```
