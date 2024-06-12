import numpy as np
import cv2 # type: ignore
from flask import Flask, request, jsonify
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
import tensorflow as tf
from firebase_admin import credentials, initialize_app, firestore # type: ignore
import utils.storage as store



# initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")

# intialize firebase
cred = credentials.Certificate("wanderer-ai.json")
initialize_app(cred, {"storageBucket": "wanderer-ai.appspot.com"})

# Load the saved model
try:
    model = tf.saved_model.load('saved_model2')
except Exception as e:
    print("Error loading model:", e)
    exit()

infer = model.signatures['serving_default']

# Load Haar cascade classifier for face detection
face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def process_frame(frame_data:bytes):
    try:
        # Decode base64 frame data
        # frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_data, np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)

        for (x, y, w, h) in faces_detected:
            # Crop the face region and resize it to match model input size
            roi_gray = gray_img[y:y + w, x:x + h]
            roi_gray = cv2.resize(roi_gray, (48, 48))

            # Convert the cropped face region to array and preprocess
            img_pixels = image.img_to_array(roi_gray)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 255

            return img_pixels

    except Exception as e:
        print("Error processing frame:", e)
        return None
    
def predict_emotion(img):
    try:
        prediction = infer(tf.constant(img))['dense_1']
        max_index = np.argmax(prediction[0])
        return max_index
    except Exception as e:
        print("Error making predictions:", e)
        return None

@app.route('/predictions/fer', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            data = request.get_json()
            session_id = data.get('sessionId')
            user_id = data.get('userId')

            # load all images for the session
            images = store.load_images(session_id)

            if len(images) == 0:
                return jsonify({'error': 'No images found for session'}), 400

            # preprocess images
            predictions = []
            bad = 0
            for img in images:
                processed_image = process_frame(img)
                if processed_image is not None:
                    prediction = infer(tf.constant(processed_image))['dense_1']
                    max_index = np.argmax(prediction[0])
                    emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
                    predicted_emotion = emotions[max_index]
                    confidence_score = np.max(prediction[0])
                    predictions.append({'emotion': predicted_emotion, 'confidence': str(confidence_score)})
                else:
                    bad += 1
            print('not processed images or none images:', bad)

            # save predictions
            res = store.save_predictions(session_id, int(user_id), predictions)

            if not res:
                return jsonify({'error': 'Error saving predictions'}), 500
            
            return jsonify({'predictions': predictions})
        except Exception as e:
            print("Error making predictions:", e)
            return jsonify({'error': 'Error making predictions', 'exception': str(e)}), 500

    return jsonify({'error': 'Invalid request'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)

