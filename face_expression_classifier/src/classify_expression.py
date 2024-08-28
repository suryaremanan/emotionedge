import numpy as np
import cv2
import tensorflow as tf

def load_model():
    return tf.keras.models.load_model('models/expression_model.h5')

def classify_expression(model, processed_faces):
    predictions = model.predict(processed_faces)
    expression_labels = ['bored', 'neutral', 'attentive']
    predicted_labels = [expression_labels[np.argmax(pred)] for pred in predictions]
    return predicted_labels

def annotate_faces(image, faces, labels):
    for (x, y, w, h), label in zip(faces, labels):
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(image, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    return image