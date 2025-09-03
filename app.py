from flask import Flask, render_template, jsonify
import tkinter as tk
from tkinter import filedialog
import os
import shutil
from utils.predict import predict_all, majority_prediction  # ✅ Use correct predict_all()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/input_images'

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Select exactly 10 fingerprint images
@app.route('/select-images', methods=['POST'])
def select_images():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        root = tk.Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        file_paths = filedialog.askopenfilenames(
            title="Select 10 fingerprint images",
            filetypes=[("BMP files", "*.BMP"), ("All files", "*.*")]
        )
        root.destroy()

        if len(file_paths) != 10:
            return jsonify({'error': 'Please select exactly 10 images.'})

        input_dir = app.config['UPLOAD_FOLDER']
        for f in os.listdir(input_dir):
            os.remove(os.path.join(input_dir, f))

        for path in file_paths:
            shutil.copy(path, os.path.join(input_dir, os.path.basename(path)))

        return jsonify({'success': True})

    except Exception as e:
        print("❌ Image Selection Error:", str(e))
        return jsonify({'error': 'Image selection failed.'})

# Predict route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_dir = app.config['UPLOAD_FOLDER']
        if len(os.listdir(input_dir)) != 10:
            return jsonify({'error': 'Please select 10 images first.'})

        predictions = predict_all(input_dir)  # ✅ Uses updated predict_all()
        final_prediction = majority_prediction(predictions)

        return jsonify({
            'success': True,
            'final_prediction': final_prediction,
            'predictions': predictions
        })

    except Exception as e:
        print("❌ Prediction Error:", str(e))
        return jsonify({'error': 'Prediction failed.'})

# Detail view for a single fingerprint (optional)
@app.route('/fingerprint-detail/<filename>')
def fingerprint_detail(filename):
    try:
        from utils.predict import predict_single_softmax
        input_dir = app.config['UPLOAD_FOLDER']
        filepath = os.path.join(input_dir, filename)
        result = predict_single_softmax(filepath)

        return render_template('fingerprint_detail.html',
                               image_file=filename,
                               confidences=result['confidence'],
                               predicted_label=result['label'])
    except Exception as e:
        print("❌ Fingerprint Detail Error:", str(e))
        return "Error loading fingerprint details.", 500

if __name__ == '__main__':
    app.run(debug=True)
