from flask import Flask, render_template, request
import os

app = Flask(__name__)

def get_subfolders_recursive(path):
    subfolders = []
    for root, dirs, _ in os.walk(path):
        for d in dirs:
            subfolders.append(os.path.relpath(os.path.join(root, d), path))
    return subfolders

def get_files_recursive(path):
    all_files = []
    for root, _, files in os.walk(path):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), path)
            all_files.append(rel_path)
    return all_files

def search_keyword_in_files(keyword, files, base_path):
    results = []
    for file in files:
        file_path = os.path.join(base_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            continue
        if keyword.lower() in content.lower():
            results.append(file)
    return results


@app.route('/')
def index():
    data_folders = get_subfolders_recursive('Data/')
    return render_template('results2.html', folders=data_folders)

@app.route('/get_folder_content', methods=['POST'])
def get_folder_content():
    selected_folder = request.form['selected_folder']
    keyword = request.form['keyword']
    folder_path = f'Data/{selected_folder}'
    all_files = get_files_recursive(folder_path)
    matched_files = search_keyword_in_files(keyword, all_files, folder_path)
    return {'folder_content': matched_files}

app.run(host='0.0.0.0', port=5000)
