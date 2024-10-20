from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify, send_file
from ultralytics import YOLO
import os
import uuid

from werkzeug.security import safe_join

app = Flask(__name__)

# Model and Upload Folder
MODEL_PATH = 'model/model.pt'
model = YOLO(MODEL_PATH)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Video Results Folder
SAVE_VIDEO_FOLDER = 'results'
os.makedirs(SAVE_VIDEO_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")

        if file:
            file_ext = os.path.splitext(file.filename)[1].lower()

            if file_ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'):  # Handle images
                filename = str(uuid.uuid4()) + file_ext
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                results = model(filepath)
                annotated_filename = "annotated_" + filename
                annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
                results[0].save(annotated_image_path)

                return redirect(url_for('show_results',
                                        original_image_name=filename,
                                        annotated_image_name=annotated_filename))

            elif file_ext in ('.mp4', '.avi', '.mov', '.mkv', '.wmv'):  # Handle videos
                video_filename = str(uuid.uuid4()) + file_ext
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
                file.save(video_path)

                processed_video_name = process_video(video_path, model)

                return redirect(url_for('show_video_results', video_name=processed_video_name))

    return render_template('index.html')


@app.route('/image_upload', methods=['POST'])
def image_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No image file uploaded.'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected image file.'})

    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        results = model(filepath, conf=0.5)
        annotated_filename = "annotated_" + filename
        annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
        results[0].save(annotated_image_path)

        return jsonify({'original_image_name': filename, 'annotated_image_name': annotated_filename})


@app.route('/video_upload', methods=['POST'])
def video_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No video file uploaded.'})

    video = request.files['file']
    if video.filename == '':
        return jsonify({'error': 'No selected video file.'})

    if video:
        video_filename = str(uuid.uuid4()) + os.path.splitext(video.filename)[1]
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video.save(video_path)

        processed_video_name = process_video(video_path, model)

        return jsonify({'video_path': processed_video_name})


@app.route('/results/<original_image_name>/<annotated_image_name>')
def show_results(original_image_name, annotated_image_name):
    return render_template('results.html',
                           original_image_name=original_image_name,
                           annotated_image_name=annotated_image_name)


@app.route('/video_results/<path:video_name>')
def show_video_results(video_name):
    return render_template('video_results.html', video_name=video_name)


def process_video(video_path, model):
    video_filename = os.path.basename(video_path)
    print("Processing this uploaded video:", video_filename)
    unique_filename = str(uuid.uuid4())
    save_directory = os.path.join(SAVE_VIDEO_FOLDER, unique_filename)
    os.makedirs(save_directory, exist_ok=True)

    results = model(video_path, conf=0.5, save=True, project=save_directory, name='processed_video',
                    exist_ok=True)

    processed_video_filename = os.path.join(unique_filename,
                                            f'processed_video/{video_filename[:-4]}.avi')
    return processed_video_filename


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/results/<path:filename>')
def download_video(filename):
    safe_video_path = safe_join(SAVE_VIDEO_FOLDER, filename)

    if not os.path.exists(safe_video_path):
        return "Error: Video not found", 404

    return send_file(safe_video_path, as_attachment=True)


@app.route('/video_feed/<path:filename>')
def video_feed(filename):
    safe_video_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(safe_video_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype='video/avi')

    else:
        return "Error: Video not found", 404


if __name__ == '__main__':
    app.run(debug=True)
