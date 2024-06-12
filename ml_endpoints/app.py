import threading
import queue
import numpy as np
import requests
import cv2 # type: ignore
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
import tensorflow as tf
from firebase_admin import credentials, initialize_app, firestore # type: ignore
import utils.storage as store
import os
import librosa
from keras.models import model_from_json # type: ignore
from keras_self_attention import SeqSelfAttention
from scipy.signal import resample

# initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")

# intialize firebase
cred = credentials.Certificate("wanderer-ai.json")
initialize_app(cred, {"storageBucket": "wanderer-ai.appspot.com"})

# Load the saved model for facial expression recognition
try:
    model = tf.saved_model.load('saved_model2')
except Exception as e:
    print("Error loading model:", e)
    exit()

infer = model.signatures['serving_default']

# Load Haar cascade classifier for face detection
face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load the saved model for speech emotion recognition
json_file = open('model_json2.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json, custom_objects={'SeqSelfAttention': SeqSelfAttention})
loaded_model.load_weights("saved_ser_model/best_model.keras")

# Emotion labels
emotion_labels = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]

def process_frame(frame_data: bytes):
    try:
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)

        for (x, y, w, h) in faces_detected:
            roi_gray = gray_img[y:y + w, x:x + h]
            roi_gray = cv2.resize(roi_gray, (48, 48))

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
        confidence = np.max(prediction[0])
        return max_index, confidence
    except Exception as e:
        print("Error making predictions:", e)
        return None

def predict_SER_emotion(audio_file, n_mfcc=30):
    try:
        y, sr = librosa.load(audio_file, mono=True, sr=None, offset=0.5, duration=2.5, dtype=np.float64, res_type='kaiser_fast')
    except Exception as e:
        error_type = e.__class__.__name__
        error_message = str(e)
        print(f"An error occurred: {error_type}: {error_message}")
        return None, str(e)
    if sr != 44100:
        y = resample(y, int(len(y) * 44100 / sr))

    try:
        mfccs = librosa.feature.mfcc(y=y, sr=44100, n_mfcc=n_mfcc)

        expected_frames = 216
        if mfccs.shape[1] < expected_frames:
            mfccs = np.pad(mfccs, ((0, 0), (0, expected_frames - mfccs.shape[1])), mode='constant')
        elif mfccs.shape[1] > expected_frames:
            mfccs = mfccs[:, :expected_frames]

        mfccs_norm = (mfccs - np.mean(mfccs)) / np.std(mfccs)
        mfccs_norm = np.expand_dims(mfccs_norm, axis=0)
        mfccs_norm = np.expand_dims(mfccs_norm, axis=-1)

        prediction = loaded_model.predict(mfccs_norm)
        emotion_index = np.argmax(prediction)
        confidence = np.max(prediction)
        emotion = emotion_labels[emotion_index]

        return confidence, emotion
    except Exception as e:
        print("Error making predictions:", e)
        return None, str(e)

def predict_fer_thread(session_id, user_id,images, q):
    with app.app_context():
        try:
            predictions = []
            bad = 0
            for img in images:
                processed_image = process_frame(img)
                if processed_image is not None:
                    prediction_index, confidence = predict_emotion(processed_image)
                    if prediction_index is not None:
                        emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
                        predicted_emotion = emotions[prediction_index]
                        prediction = {'emotion': predicted_emotion, 'confidence': str(confidence)}
                        predictions.append(prediction)
                    else:
                        bad += 1
            print('not processed images or none images:', bad)
            store.save_predictions(session_id, int(user_id), predictions, type='fer')
            q.put({'message': 'FER predictions completed'})
        except Exception as e:
            print("Error in predict_fer_thread:", e)
            q.put({'error': str(e)})

def predict_ser_thread(session_id, user_id, audio_files_dir, q):
    with app.app_context():
        try:
            prediction_results = []
            for filename in os.listdir(audio_files_dir):
                if filename.endswith('.wav'):
                    audio_file = os.path.join(audio_files_dir, filename)
                    confidence, emotion = predict_SER_emotion(audio_file)
                    print(emotion)
                    if confidence is not None:
                        prediction_results.append({'filename': filename, 'confidence': str(confidence), 'emotion': emotion})

            if not prediction_results:
                q.put({'message': 'SER predictions not ready'})
                return

            store.save_predictions(session_id, user_id, prediction_results, type='ser')

            for filename in os.listdir(audio_files_dir):
                os.remove(os.path.join(audio_files_dir, filename))
            q.put({'message': 'SER predictions completed'})
        except Exception as e:
            print("Error in predict_ser_thread:", e)
            q.put({'error': str(e)})



@app.before_request
def verify_api_key():
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key != 'wanderer1234@WERTYYY5666FF':
        return jsonify({'error': 'Invalid API key.'}), 401



@app.route('/predictions/all', methods=['POST'])
def predict_all():
    if request.method == 'POST':
        try:
            data = request.get_json()
            session_id = data.get('sessionId')
            user_id = data.get('userId')
            callback_url = data.get('callbackUrl')  # Get callback URL from request for webhooking

            audio_files_dir = store.download_audio_files(session_id)
            images = store.load_images(session_id)


            q = queue.Queue()

            thread1 = threading.Thread(target=predict_fer_thread, args=(session_id, user_id, images, q))
            thread2 = threading.Thread(target=predict_ser_thread, args=(session_id, user_id, audio_files_dir, q))

            thread1.start()
            thread2.start()

            thread1.join()
            thread2.join()

            results = []
            while not q.empty():
                results.append(q.get())

            
            # Make POST request to the callback URL with the predictions
            callback_data = {'sessionId': session_id, 'userId': user_id, 'status': 'completed'}
            res = requests.post(callback_url, json=callback_data)

            if res.status_code != 200:
                return jsonify({'error': 'Error starting or completing predictions', 'exception': str(res.text)}), 500

            return jsonify({'message': 'success', 'results': results}), 200

        except Exception as e:
            print("Error in predict_all:", e)
            # Make POST request to the callback URL with the predictions
            callback_data = {'sessionId': session_id, 'userId': user_id, 'status': 'aborted'}
            requests.post(callback_url, json=callback_data)
            return jsonify({'error': 'Error starting or completing predictions', 'exception': str(e)}), 500

    return jsonify({'error': 'Invalid request'})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
