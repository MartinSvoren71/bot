from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    data_folders = os.listdir('Data/')
    return render_template('results2.html', folders=data_folders)

@app.route('/get_folder_content', methods=['POST'])
def get_folder_content():
    selected_folder = request.form['selected_folder']
    folder_content = os.listdir(f'Data/{selected_folder}')
    return {'folder_content': folder_content}

app.run(host='0.0.0.0', port=5000)

