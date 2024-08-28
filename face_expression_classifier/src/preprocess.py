import numpy as np
import cv2
from sklearn.model_selection import train_test_split
import os

def load_and_preprocess_images(image_dir, image_size=(64, 64)):
    images = []
    labels = []
    label_map = {'bored': 0, 'neutral': 1, 'attentive': 2}
    
    for label, idx in label_map.items():
        label_dir = os.path.join(image_dir, label)
        for image_name in os.listdir(label_dir):
            image_path = os.path.join(label_dir, image_name)
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            image = cv2.resize(image, image_size)
            image = image / 255.0
            images.append(image)
            labels.append(idx)
    
    images = np.array(images).reshape(-1, image_size[0], image_size[1], 1)
    labels = np.array(labels)
    
    return train_test_split(images, labels, test_size=0.2, random_state=42)