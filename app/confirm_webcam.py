import cv2

def test_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
    else:
        print("Webcam initialized successfully.")
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Webcam Test', frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        cap.release()

if __name__ == "__main__":
    test_webcam()
