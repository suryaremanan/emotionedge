import pickle

with open("/home/surya-remanan/Desktop/MindSparksAI/app/models/encodings.pkl", "rb") as f:
    known_face_encodings, known_face_names = pickle.load(f)

print(known_face_names)
print(len(known_face_encodings))
