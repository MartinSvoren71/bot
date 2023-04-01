from flask import Flask, render_template, request
import os

app = Flask(__name__)

def get_subfolders(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

@app.route('/')
def index():
    data_folders = get_subfolders('Data/')
    return render_template('index.html', folders=data_folders)

@app.route('/get_folder_content', methods=['POST'])
def get_folder_content():
    selected_folder = request.form['selected_folder']
    folder_path = f'Data/{selected_folder}'
    folder_content = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return {'folder_content': folder_content}

app.run(host='0.0.0.0', port=5000)

