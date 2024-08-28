For our real-time engagement monitoring system, we have focused on detecting three primary emotional states: **`bored, neutral, and attentive`**. This initial setup serves as a demonstrative model, showcasing the core functionality of our system. As we scale, more nuanced emotional states can be incorporated to provide an even deeper understanding of student engagement.

Our approach utilizes Haar Cascades for initial face detection, followed by a Convolutional Neural Network (CNN) model built with the TensorFlow framework to accurately classify these emotional states. This combination ensures reliable real-time monitoring and lays a solid foundation for future enhancements. 

By leveraging these advanced techniques, our system aims to provide teachers with immediate insights into student engagement, enabling timely interventions and fostering a more interactive and effective learning environment.

### Technical Implementation

1. Create a python virtual environment using the following command:
		`python3 -m venv faces`
2. Activate the environment:
		`source faces/bin/activate`
3. Install all the dependencies in the file `requirements.txt`
		`pip install -r requirements.txt`
4. The `requirements.txt` file contains following libraries:
```
opencv-python
dlib
tensorflow
numpy
scikit-learn
```
5. Run the script for training:
```
python main.py
```

