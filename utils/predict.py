import os
import numpy as np
import cv2
import tensorflow as tf

# Load model once
MODEL_PATH = r'C:\Users\dell\Desktop\fingeprint_demo\model\final_best_efficientnetb0_model_final.keras'
model = tf.keras.models.load_model(MODEL_PATH)

CLASS_LABELS = ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']
TARGET_SIZE = (103, 96)

# Preprocess a single fingerprint image
def preprocess_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, TARGET_SIZE)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=-1)
    img = np.repeat(img, 3, axis=-1)
    img = np.expand_dims(img, axis=0)
    return img

# Predict all 10 images
def predict_all(image_dir):
    predictions = []
    for filename in sorted(os.listdir(image_dir)):
        if filename.lower().endswith('.bmp'):
            full_path = os.path.join(image_dir, filename)
            img_tensor = preprocess_image(full_path)
            preds = model.predict(img_tensor, verbose=0)[0]  # shape: (8,)
            label = CLASS_LABELS[np.argmax(preds)]

            predictions.append({
                "filename": os.path.basename(filename),
                "label": label,
                "confidence": preds.tolist()  # list of 8 softmax scores
            })
    return predictions

# Majority voting
def majority_prediction(predictions):
    labels = [p['label'] for p in predictions]
    return max(set(labels), key=labels.count)

# Predict a single image (optional detail route)
def predict_single_softmax(img_path):
    img_tensor = preprocess_image(img_path)
    preds = model.predict(img_tensor, verbose=0)[0]
    label_index = int(np.argmax(preds))
    label = CLASS_LABELS[label_index]

    return {
        'filename': os.path.basename(img_path),
        'label': label,
        'confidence': preds.tolist()
    }
