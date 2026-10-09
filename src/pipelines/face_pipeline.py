import dlib
import numpy as np
import face_recognition_models
from functools import lru_cache
from typing import Optional, Dict, Any, List

from src.database.db import get_all_students

RESEMBLANCE_THRESHOLD = 0.55
DETECTOR_UPSAMPLE_TIMES = 2

# Global cached classifier data
_TRAINED_MODEL_CACHE: Optional[Dict[str, Any]] = None

@lru_cache(maxsize=1)
def load_dlib_models():
    """Load dlib frontal face detector and 128-d neural shape/face predictor."""
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector, sp, facerec

def get_face_embeddings(image_np):
    """Extract 128-d facial vector descriptors from an image array."""
    detector, sp, facerec = load_dlib_models()
    image_np = np.ascontiguousarray(image_np[:, :, :3].astype(np.uint8))
    faces = detector(image_np, DETECTOR_UPSAMPLE_TIMES)

    encodings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)  # 128-d vector
        encodings.append(np.array(face_descriptor))
    return encodings

def get_trained_model():
    """Retrieve or compute cached enrolled student embeddings."""
    global _TRAINED_MODEL_CACHE
    if _TRAINED_MODEL_CACHE is not None:
        return _TRAINED_MODEL_CACHE

    X = []
    y = []
    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) == 0:
        return None

    _TRAINED_MODEL_CACHE = {'X': X, 'y': y}
    return _TRAINED_MODEL_CACHE

def train_classifier():
    """Clear memory cache and reload enrolled student vectors."""
    global _TRAINED_MODEL_CACHE
    _TRAINED_MODEL_CACHE = None
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np, allow_single_student=False, candidate_student_ids=None):
    """Identify students present in classroom image via Euclidean distance match."""
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = get_trained_model()
    if not model_data:
        return detected_student, [], len(encodings)

    X_train = model_data['X']
    y_train = model_data['y']

    if candidate_student_ids is not None:
        candidate_student_ids = {int(student_id) for student_id in candidate_student_ids}
        candidate_pairs = [
            (embedding, student_id)
            for embedding, student_id in zip(X_train, y_train)
            if int(student_id) in candidate_student_ids
        ]

        if not candidate_pairs:
            return detected_student, [], len(encodings)

        X_train = [pair[0] for pair in candidate_pairs]
        y_train = [pair[1] for pair in candidate_pairs]

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students) < 2 and not allow_single_student:
            return {}, all_students, len(encodings)

        distances = np.linalg.norm(np.array(X_train) - encoding, axis=1)
        best_match_index = int(np.argmin(distances))
        best_match_score = float(distances[best_match_index])
        predicted_id = int(y_train[best_match_index])

        if best_match_score <= RESEMBLANCE_THRESHOLD:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)
