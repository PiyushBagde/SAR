from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from ultralytics import YOLO
import os

app = Flask(__name__)
MODEL_PATH = 'model/model.pt'
model = YOLO(MODEL_PATH)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")

        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            results = model(filepath, conf=0.7)

            annotated_filename = 'annotated_' + filename
            annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            results[0].save(annotated_image_path)

            return redirect(url_for('show_results',
                                    original_image_name=filename,
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
