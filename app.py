from flask import Flask, render_template, request, send_from_directory
from ultralytics import YOLO
import os

app = Flask(__name__)
MODEL_PATH = 'model/best.pt'  # Path to your .pt model
model = YOLO(MODEL_PATH)  # Load the model once, globally

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create uploads directory if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")
        if file:  # Check if the file is actually uploaded
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Run inference
            results = model(filepath)  # Results object with predictions

            # Save annotated image
            annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'annotated_' + file.filename)
            results[0].save(annotated_image_path)  # Save the first image (index 0)

            return render_template('index.html', image_path='uploads/annotated_' + file.filename)

    return render_template('index.html')


# Serving uploaded/processed files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
