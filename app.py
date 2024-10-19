from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
from ultralytics import YOLO
import os
import uuid
import time

app = Flask(__name__)

# Model and Upload Folder Setup
MODEL_PATH = 'model/model.pt'  # Update with your model path
model = YOLO(MODEL_PATH)  # Load the YOLO model

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")

        if file:
            # Generate unique filenames
            filename = file.filename
            extension = os.path.splitext(filename)[1]  # Get file extension
            original_filename = str(uuid.uuid4()) + extension
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            file.save(filepath)

            # --- Perform YOLOv8 inference ---
            results = model(filepath, conf=0.5)

            # Save annotated image with unique filename
            annotated_filename = "annotated_" + original_filename
            annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            results[0].save(annotated_image_path)  # Save the first annotated image
            # -------------------------------

            # Redirect to the results page
            return redirect(url_for('show_results',
                                    original_image_name=original_filename,
                                    annotated_image_name=annotated_filename))

    return render_template('index.html')


@app.route('/results/<original_image_name>/<annotated_image_name>')
def show_results(original_image_name, annotated_image_name):
    return render_template('results.html',
                           original_image_name=original_image_name,
                           annotated_image_name=annotated_image_name)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
