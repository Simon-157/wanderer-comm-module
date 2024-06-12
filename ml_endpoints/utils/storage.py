import os
import zipfile
from firebase_admin import firestore, storage # type: ignore
from datetime import datetime

def download_audio_files(session_id):
    bucket = storage.bucket()

    audio_files_dir = 'audio_files'
    if not os.path.exists(audio_files_dir):
        os.makedirs(audio_files_dir)

    blobs = bucket.list_blobs(prefix=session_id + '/audio/')
    for blob in blobs:
        if blob.name.endswith('.wav') and blob.content_type == 'audio/wav': 
            blob.download_to_filename(os.path.join(audio_files_dir, os.path.basename(blob.name)))

    return audio_files_dir


def load_images(session_id):
    bucket = storage.bucket()
    images = []
    blobs = bucket.list_blobs(prefix=session_id + '/frame/')
    for blob in blobs:
        if blob.name.endswith('.jpg'):
            
            images.append(blob.download_as_bytes())
    print('Number of images:', len(images))
    return images



def zip_audio_files(directory):
    zip_file_name = 'audio_files.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))
    return zip_file_name



def save_predictions(session_id, user_id, predictions, type):
    print(user_id, session_id)
    try:
        db = firestore.client()
    except Exception as e:
        print("Error connecting to Firestore:", e)
        return False, e
    try:
        session_ref = db.collection('users').document(str(user_id)).collection('sessions').document(session_id)
        batch = db.batch()

        timestamp = datetime.now()

        for prediction in predictions:
            
            doc_ref = session_ref.collection('ser-emotions').document() if type == 'ser' else doc_ref == session_ref.collection('fer-emotions').document()

            doc_data = {
                'filename': prediction['filename'],
                'confidence': prediction['confidence'],
                'emotion': prediction['emotion'],
                'timestamp': timestamp
            }

            batch.set(doc_ref, doc_data)

        # Commit the batched writes
        batch.commit()

    except Exception as e:
        print("Error saving predictions:", e)
        return False, e

    return True, None
   