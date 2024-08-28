import cv2
import requests
import time

def capture_and_send_frame():
    cap = None
    for index in range(5):  # Try the first 5 indices
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Opened camera at index {index}")
            break
    else:
        print("Failed to open any camera")
        return

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                _, img_encoded = cv2.imencode('.jpg', frame)
                try:
                    upload_response = requests.post(
                        "http://localhost:8000/upload_image/",
                        files={'file': ('image.jpg', img_encoded.tobytes(), 'image/jpeg')}
                    )
                    if upload_response.status_code == 200:
                        upload_data = upload_response.json()
                        image_id = upload_data["image_id"]
                        
                        recognize_response = requests.post(
                            f"http://localhost:8000/recognize_image/{image_id}"
                        )
                        if recognize_response.status_code == 200:
                            print(recognize_response.json())
                        else:
                            print(f"Recognition request failed with status code {recognize_response.status_code}")
                    else:
                        print(f"Upload request failed with status code {upload_response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
            else:
                print("Failed to capture frame")
            time.sleep(1)  # Capture frame every second to avoid overwhelming the server

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        cap.release()

if __name__ == "__main__":
    capture_and_send_frame()
