from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Data'
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    folders = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', folders=folders)

@app.route('/files', methods=['POST'])
def list_files():
    selected_folder = request.form.get('selected_folder')
    if selected_folder:
        file_list = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], selected_folder))
        return {'files': file_list, 'selected_folder': selected_folder}
    return {'error': 'No folder selected'}

app.run(host='0.0.0.0', port=5000)

