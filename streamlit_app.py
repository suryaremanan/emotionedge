import streamlit as st
import cv2
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
import time

st.title("MindSparksAI")

# Attempt to connect to FastAPI with retries
max_retries = 5
for i in range(max_retries):
    try:
        response = requests.get("http://fastapi:8000/known_faces/")
        if response.status_code == 200:
            known_faces = response.json().get("known_faces", [])
            break
    except requests.exceptions.ConnectionError:
        if i < max_retries - 1:
            time.sleep(3)  # Wait for a few seconds before retrying
        else:
            st.error("Failed to connect to FastAPI.")
            known_faces = []

selected_student = st.selectbox("Select a student", known_faces)

# Onboard a new student
st.header("Onboard a New Student")
student_name = st.text_input("Enter the student's name")
uploaded_image = st.file_uploader("Upload a student's image", type=["jpg", "jpeg", "png"])

if st.button("Onboard Student"):
    if student_name and uploaded_image:
        files = {"file": (uploaded_image.name, uploaded_image.read(), uploaded_image.type)}
        data = {"student_name": student_name}
        response = requests.post("http://fastapi:8000/onboard_student/", files=files, data=data)
        if response.status_code == 200:
            st.success(f"Successfully onboarded {student_name}")
        else:
            st.error("Failed to onboard the student.")
    else:
        st.error("Please enter the student's name and upload an image.")

# Initialize the webcam and emotion detection
st.header("Emotion Detection")
run = st.checkbox('Run')

if run:
    # Create placeholders for the video stream and gauges
    video_capture = st.empty()
    gauge_placeholder = st.empty()
    emotion_history_placeholder = st.empty()
    frame_count = 0  # Add a frame count to generate unique keys

    # Capture video from the webcam
    cap = cv2.VideoCapture(0)

    while run:
        ret, frame = cap.read()
        if not ret:
            st.write("Failed to capture frame")
            continue

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Display the frame
        video_capture.image(frame_rgb, channels="RGB")

        # Convert frame to JPEG format
        is_success, buffer = cv2.imencode(".jpg", frame)
        io_buf = io.BytesIO(buffer)

        # Send the frame to FastAPI for processing
        response = requests.post("http://fastapi:8000/upload_image/", files={"file": ("frame.jpg", io_buf.getvalue(), "image/jpeg")})
        if response.status_code == 200:
            image_id = response.json().get("image_id")
            recognition_response = requests.post(f"http://fastapi:8000/recognize_image/{image_id}")
            recognition_data = recognition_response.json()
            name = recognition_data.get("name")
            emotion = recognition_data.get("emotion")

            if name == selected_student:
                # Update gauge level based on emotion
                emotion_levels = {"Bored": 0, "Neutral": 1, "Attentive": 2}
                gauge_value = emotion_levels.get(emotion, 0)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=gauge_value,
                    title={'text': f"{selected_student}'s Emotion Gauge"},
                    gauge={'axis': {'range': [0, 2]},
                           'steps': [
                               {'range': [0, 1], 'color': "lightgray"},
                               {'range': [1, 2], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 2}}))

                gauge_placeholder.plotly_chart(fig)

                # Fetch historical emotions for the bar chart
                emotions_response = requests.get(f"http://fastapi:8000/emotions/{selected_student}")
                if emotions_response.status_code == 200:
                    emotions_data = emotions_response.json().get("emotions")
                    df = pd.DataFrame(emotions_data)
                    emotion_histogram = px.histogram(df, x='emotion', title=f"{selected_student}'s Emotion History")
                    emotion_history_placeholder.plotly_chart(emotion_histogram)

        else:
            st.write("Error uploading the image or processing the request.")

        frame_count += 1  # Increment the frame count to ensure unique keys

    cap.release()
else:
    st.write("Streaming Stopped.")

# Add Recommendations section
if st.button('Generate Recommendations'):
    recommendations_response = requests.get(f"http://fastapi:8000/recommendations/{selected_student}")
    if recommendations_response.status_code == 200:
        recommendations = recommendations_response.json().get("recommendations")
        if isinstance(recommendations, list):
            st.write("Recommendations:")
            for recommendation in recommendations:
                st.write(f"- {recommendation}")
        else:
            st.write(f"Recommendations: {recommendations}")
    else:
        st.write("Error fetching recommendations")
