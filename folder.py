from flask import Flask, render_template, request, redirect, url_for, flash
import os
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/')
def index():
    folders = [f for f in os.listdir("Data/") if os.path.isdir(os.path.join("Data/", f))]
    return render_template('index.html', folders=folders)

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

if __name__ == '__main__':
    app.run(debug=True)
