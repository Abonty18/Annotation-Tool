# __init__.py or any other initialization file
import os
import joblib
from django.conf import settings

model_path = settings.MODEL_FILES_DIR
best_logreg_model = joblib.load(os.path.join(model_path, 'best_logreg_model.pkl'))
scaler = joblib.load(os.path.join(model_path, 'scaler.pkl'))
tfidf_vectorizer = joblib.load(os.path.join(model_path, 'tfidf_vectorizer.pkl'))
label_encoder = joblib.load(os.path.join(model_path, 'label_encoder.pkl'))
