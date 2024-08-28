from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from app.utils import load_models, preprocess_image
from app.database import SessionLocal, Emotion
from app.recommendation import generate_recommendations
from app.report import generate_pdf_report
from generate_encodings import generate_encodings
import numpy as np
import cv2
import face_recognition
import logging
from pathlib import Path
import os
from pathlib import Path

# Ensure the models directory exists
MODELS_DIR = Path("app/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
# Configure logging
logging.basicConfig(level=logging.INFO)

# Directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploaded_images"))
KNOWN_FACES_DIR = Path(os.getenv("KNOWN_FACES_DIR", "known_faces"))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "reports"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load models at startup
emotion_model, known_face_encodings, known_face_names = None, None, None

@app.on_event("startup")
async def startup_event():
    global emotion_model, known_face_encodings, known_face_names
    emotion_model, known_face_encodings, known_face_names = load_models()
    logging.info("Models loaded successfully.")
    logging.info("Starting the FastAPI server...")

@app.get("/")
def read_root():
    return {"message": "Welcome to MindsparksAI"}

@app.get("/known_faces/")
def get_known_faces():
    return {"known_faces": known_face_names}

@app.post("/onboard_student/")
async def onboard_student(student_name: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        image_path = KNOWN_FACES_DIR / f"{student_name}.jpg"
        
        # Save the student's image
        with open(image_path, "wb") as f:
            f.write(content)
        logging.info(f"Saved student image at {image_path}")

        # Generate face encodings dynamically
        encodings_path = "app/models/encodings.pkl"  # Use a relative path
        generate_encodings(str(KNOWN_FACES_DIR), str(encodings_path))
        
        # Reload models after updating encodings
        global known_face_encodings, known_face_names
        _, known_face_encodings, known_face_names = load_models()

        return {"message": f"Student {student_name} onboarded successfully."}
    except Exception as e:
        logging.error(f"Error onboarding student: {e}")
        raise HTTPException(status_code=500, detail="Failed to onboard student")

@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image_path = UPLOAD_DIR / file.filename
        with open(image_path, "wb") as f:
            f.write(content)
        logging.info(f"Image saved at {image_path}")
        return JSONResponse(content={"message": "Image uploaded successfully", "image_id": file.filename})
    except Exception as e:
        logging.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/recognize_image/{image_id}")
async def recognize_image(image_id: str, db: Session = Depends(get_db)):
    try:
        image_path = UPLOAD_DIR / image_id
        img = cv2.imread(str(image_path))
        
        if img is None:
            raise HTTPException(status_code=400, detail="Image not found")

        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)
        name = "Unknown"
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                break

        if face_locations:
            top, right, bottom, left = face_locations[0]
            face_img = img[top:bottom, left:right]
            processed_face = preprocess_image(face_img)
            emotion_prediction = emotion_model.predict(processed_face)[0]

            emotion_labels = {0: "Bored", 1: "Neutral", 2: "Attentive"}
            emotion = emotion_labels[np.argmax(emotion_prediction)]
        else:
            emotion = "No face detected"

        db_emotion = Emotion(name=name, emotion=emotion)
        db.add(db_emotion)
        db.commit()
        db.refresh(db_emotion)

        return JSONResponse({
            "name": name,
            "emotion": emotion
        })

    except Exception as e:
        logging.error(f"Error during recognition: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/recommendations/{student_name}")
def get_recommendations(student_name: str, db: Session = Depends(get_db)):
    try:
        emotions = db.query(Emotion).filter(Emotion.name == student_name).all()
        emotion_list = [e.emotion for e in emotions]
        recommendations = generate_recommendations(student_name, emotion_list)
        return {"student_name": student_name, "recommendations": recommendations}
    except Exception as e:
        logging.error(f"Error while generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/emotions/{student_name}")
def get_emotions(student_name: str, db: Session = Depends(get_db)):
    try:
        emotions = db.query(Emotion).filter(Emotion.name == student_name).all()
        emotion_data = [{"timestamp": e.timestamp, "emotion": e.emotion} for e in emotions]
        return {"student_name": student_name, "emotions": emotion_data}
    except Exception as e:
        logging.error(f"Error fetching emotions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/generate_report/{student_name}")
async def generate_report_endpoint(student_name: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        emotions = db.query(Emotion).filter(Emotion.name == student_name).all()
        emotion_list = [e.emotion for e in emotions]
        recommendations = generate_recommendations(student_name, emotion_list)
        if "Error" in recommendations:
            raise HTTPException(status_code=500, detail=recommendations)

        file_name = REPORTS_DIR / f"{student_name}_report.pdf"
        background_tasks.add_task(generate_pdf_report, student_name, recommendations)
        return JSONResponse(content={"message": "Report generation started", "file_name": str(file_name)})
    except Exception as e:
        logging.error(f"Error while generating report: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/download_report/{file_name}")
async def download_report(file_name: str):
    file_path = REPORTS_DIR / file_name
    if file_path.exists():
        return FileResponse(path=str(file_path), filename=file_name, media_type='application/pdf')
    else:
        raise HTTPException(status_code=404, detail="Report not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
