import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

@app.route('/')
@app.route('/<path:subpath>')
def file_manager(subpath=None):
    if subpath:
        dir_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
    else:
        dir_path = app.config['UPLOAD_FOLDER']

    if not os.path.exists(dir_path):
        flash('Directory not found.')
        return redirect(url_for('file_manager'))

    items = os.listdir(dir_path)
    files = []
    folders = []

    for item in items:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)

    return render_template('file_manager.html', files=files, folders=folders, subpath=subpath)

@app.route('/upload/', methods=['POST'])
@app.route('/upload/<path:subpath>', methods=['POST'])
def upload(subpath=None):
    if request.method == 'POST':
        file = request.files['file']
        if file:
            if subpath:
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
            else:
                save_path = app.config['UPLOAD_FOLDER']

            file.save(os.path.join(save_path, file.filename))
            flash('File uploaded successfully.')
            return redirect(url_for('file_manager', subpath=subpath))
    flash('Error uploading file.')
    return redirect(url_for('file_manager', subpath=subpath))

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
