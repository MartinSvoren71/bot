from flask import Flask, render_template, request, redirect, url_for, flash
import os
import shutil
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
@app.route('/')
def index():
    files = os.listdir()
    return render_template('folder.html', files=files)
@app.route('Data/', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(filename)
    flash('File uploaded successfully!')
    return redirect(url_for('index'))
@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(filename)
    flash('File deleted successfully!')
    return redirect(url_for('index'))


#runn app as local on port 5000 , accesible on private and public AWS IP
app.run(host='0.0.0.0', port=5000)