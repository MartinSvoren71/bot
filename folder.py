from flask import Flask, render_template, request, redirect, url_for, flash
import os
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/')
def index():
    folders = [f for f in os.listdir("Data/") if os.path.isdir(os.path.join("Data/", f))]
    results = {}  # Define a dictionary called 'results'
    search_term = request.args.get('search_term', '')
    if search_term:
        for folder in folders:
            folder_path = os.path.join("Data/", folder)
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if search_term in content:
                            if folder_path not in results:
                                results[folder_path] = []
                            results[folder_path].append(file_path)
    return render_template('index.html', folders=folders, results=results)  # Pass 'results' to the template context


@app.route('/upload', methods=['POST'])
def upload_file():
    folder = request.form['folder']
    new_folder = request.form['new_folder']
    if new_folder:
        os.mkdir(os.path.join("Data/", folder, new_folder))
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join("Data/", folder, filename))
    flash('File uploaded successfully!')
    return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join("Data/", filename))
    flash('File deleted successfully!')
    return redirect(url_for('index'))

app.run(host='0.0.0.0', port=5000)
