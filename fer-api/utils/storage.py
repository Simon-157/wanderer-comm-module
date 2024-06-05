from firebase_admin import firestore, storage # type: ignore
from datetime import datetime


def save_predictions(session_id, user_id, predictions):
    try:
        db = firestore.client()
    except Exception as e:
        print("Error connecting to Firestore:", e)
        return False

    try:
        session_ref = db.collection('users').document(user_id).collection('sessions').document(session_id)
        batch = db.batch()

        timestamp = datetime.now()

        for prediction in predictions:
            doc_ref = session_ref.collection('fer-emotions').document()

            doc_data = {
                'confidence': prediction['confidence'],
                'emotion': prediction['emotion'],
                'timestamp': timestamp
            }

            batch.set(doc_ref, doc_data)

        # Commit the batched writes
        batch.commit()

    except Exception as e:
        print("Error saving predictions:", e)
        return False

    return True


def load_images(session_id):
    bucket = storage.bucket()
    images = []
    blobs = bucket.list_blobs(prefix=session_id + '/frame/')
    for blob in blobs:
        if blob.name.endswith('.jpg'):
            
            images.append(blob.download_as_bytes())
    print('Number of images:', len(images))
    return images

