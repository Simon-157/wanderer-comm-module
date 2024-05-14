import os
import librosa
import numpy as np
from keras.models import model_from_json # type: ignore
from keras_self_attention import SeqSelfAttention
from scipy.signal import resample
from flask import Flask, request, jsonify
from flask_cors import CORS
import utils.storage as store
from firebase_admin import credentials, initialize_app # type: ignore

# intialize firebase
cred = credentials.Certificate("wanderer-ai.json")
initialize_app(cred, {"storageBucket": "wanderer-ai.appspot.com"})

# Load the saved model
json_file = open('model_json2.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json, custom_objects={'SeqSelfAttention': SeqSelfAttention})
loaded_model.load_weights("saved_ser_model/best_model.keras")

# emotion labels
emotion_labels = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]

app = Flask(__name__)
CORS(app, origins="*")

def predict_emotion(audio_file, n_mfcc=30):
    try:
        y, sr = librosa.load(audio_file, sr=None, mono=True, offset=1.0, duration=5.0, dtype=np.float64)
    except Exception as e:
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
        return None, str(e)

@app.before_request
def verify_api_key():
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key != 'wanderer1234@WERTYYY5666FF':
        return jsonify({'error': 'Invalid API key.'}), 401

@app.route('/predict/ser', methods=['POST'])
def predict():
    if request.method != 'POST':
        return jsonify({'error': 'Invalid request method.'}), 400

    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        user_id = data.get('userId')
        audio_files_dir = store.download_audio_files(session_id)

        prediction_results = []
        for filename in os.listdir(audio_files_dir):
            if filename.endswith('.wav'):
                audio_file = os.path.join(audio_files_dir, filename)
                confidence, emotion = predict_emotion(audio_file)
                if confidence is not None:
                    prediction_results.append({'filename': filename, 'confidence': str(confidence), 'emotion': emotion})

        if not prediction_results:
            return jsonify({'message': 'success', 'status': 'not ready'}), 200

        if not store.save_predictions(session_id, user_id, prediction_results):
            return jsonify({'error': 'Error saving predictions'}), 500

        for filename in os.listdir(audio_files_dir):
            os.remove(os.path.join(audio_files_dir, filename))
        return jsonify({'message': 'success', 'status': 'ready'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/zip', methods=['POST'])
def zip():
    if request.method == 'POST':
        try:
           data = request.get_json()
           session_id = data.get('sessionId')

           if not session_id:
               return jsonify({'error': 'No session ID provided.'}), 400

           audio_files_dir = store.download_audio_files(session_id)
           zip_file_name = store.zip_audio_files(audio_files_dir)

           return jsonify({'zip_file_name': zip_file_name}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid request method.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5002)
