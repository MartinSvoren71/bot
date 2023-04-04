import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file_manager/')
def file_manager():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('file_manager.html', files=files)

@app.route('/upload/', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            flash('File uploaded successfully.')
            return redirect(url_for('file_manager'))
    flash('Error uploading file.')
    return redirect(url_for('file_manager'))

@app.route('/delete/<path:filename>')
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully.')
    else:
        flash('File not found.')
    return redirect(url_for('file_manager'))

app.run(host='0.0.0.0', port=5000)
