from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_file
from ask_ai import  ask_ai
from ask_GPT import initialize_GPT, ask_GPT
from threading import Thread
from main import api_kx
from datetime import timedelta
import os
import re
import json
import subprocess
import boto3
from PyPDF4 import PdfFileReader, PdfFileWriter
import io 
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import logging
import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import shutil
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import send_from_directory
from concurrent.futures import ThreadPoolExecutor
from pdfminer.high_level import extract_text


app = Flask(__name__, static_folder='/')
app.secret_key = "xxx007"
app.secret_key2 = "xxx707"
app.config['UPLOAD_FOLDER'] = 'Data/'
current_folder = 'Data/'

#main landign page - login 
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["key"]
        if password == app.secret_key :
            session["logged_in"] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=1)
            return redirect(url_for("index"))
        elif password == app.secret_key2 :
            session["logged_in"] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=1)
            return redirect(url_for("file_manager"))
        else:
            flash("Bad key provided")
            return redirect(url_for("bad_key"))
    return render_template("login.html")
@app.route("/bad_key")


#when bed klogin key provided
def bad_key():
    return render_template("badkey.html")


#list files from Data into web app
@app.route("/get_updated_files", methods=["GET", "POST"])
def list_files_and_urls(folder_path):
    files = []
    for root, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if not filename.startswith('.'):  # Ignore hidden files
                file = {}
                file["Key"] = os.path.join(root, filename)
                file["PresignedURL"] = url_for("static", filename=file["Key"])
                files.append(file)
    return files

# main web app wehn righ key is provided
@app.route("/indexSplit", methods=["GET", "POST"])
def index():
    if "logged_in" in session:
        data_folders = get_subfolders_recursive('Data/')
        folder_path = "Data/Coherent/Chameleon/"   # those are used for listing pdf files 
        files = list_files_and_urls(folder_path)
        folders = list_folders()
        return render_template("indexSplit.html", folders=data_folders, files=files, results={})
    else:
        flash("Please log in first")
        return redirect(url_for("login"))

# provide log.txt with open ai results of queries 
@app.route('/log-content')
def log_content():
    file_path = os.path.join(os.getcwd(), 'log.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    return content




# runn ask openai GPT / button trigger   
@app.route('/ask_gpt', methods=['POST'])
def ask_GPT_route():
    key = "nnp"

    question = request.form['question']
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_GPT(question) 
        #return jsonify({"question": question, "response": response})
            #return render_template('indexSplit.html', question=question, response=response, key=key, files=files)
    else:
        return render_template('bad_key.html')
    
    
    
    
# run ask llama index on top of custom data / button trigger   
@app.route('/ask_lib', methods=['POST'])
def ask_LIB_route():
    question = request.form['question']
    model = "text-davinci-003"
    key = "nnp"
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_ai(question, current_folder) 
    else:
        return render_template('bad_key.html')

# part_1 process search on pdf files
def process_pdf_file(filepath, keyword, pattern):
    matches = []
    is_encrypted = False

    try:
        text = extract_text(filepath, password='', codec='utf-8')
        pages = text.split('\f')

        for page_num, page_text in enumerate(pages):
            for match in pattern.finditer(page_text):
                matches.append((page_num, match.start()))

    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        if 'file has not been decrypted' in str(e):
            is_encrypted = True
        return filepath, matches, is_encrypted

    return filepath, matches, is_encrypted

# part_2 process search on pdf files     
def search_pdf_files(keyword, folder_path):
    results = {}
    encrypted_files = []
    pattern = re.compile(r'(?<=\.)([^.]*\b{}\b[^.]*(?:\.[^.]*){{0,1}})'.format(keyword))

    pdf_files = [os.path.join(root, filename)
                 for root, _, filenames in os.walk(folder_path)
                 for filename in filenames
                 if filename.lower().endswith('.pdf')]

    with ThreadPoolExecutor() as executor:
        future_results = [executor.submit(process_pdf_file, filepath, keyword, pattern) for filepath in pdf_files]

        for future in future_results:
            filepath, matches, is_encrypted = future.result()
            if is_encrypted:
                encrypted_files.append(filepath)
            elif matches:
                results[filepath] = matches

    return results, encrypted_files




# part_3 process search on pdf files     + caller from web app
@app.route('/search_pdf_files', methods=['POST'])
def search_files():
    search_results = {}
    encrypted_files = []
    
    # Set the folder path to search for PDF files
    select_folder = ''
    folder_path = f'Data/{current_folder}'
    print(f"Selected folder for search: {current_folder}")  # Print the selected folder in the terminal
    
    if request.method == 'POST':
        keyword = request.form['keyword']
        
        search_results, encrypted_files = search_pdf_files(keyword, folder_path)
        
        # Write search results to a text file
        with open('search_results.txt', 'a') as f:  # Change mode to 'a' to append to the file
            f.write(f"Search keyword: {keyword}\n")
            for filepath, matches in search_results.items():
                f.write(f"{filepath}\n")
                for page_num, match in matches:
                    f.write(f"  Page {page_num + 1}: {match}\n")
                f.write(os.linesep)
            f.write('-' * 80 + '\n')  # Add a separator line between different search results

    rendered_template = render_template('results.html', results=search_results, encrypted_files=encrypted_files)
    return jsonify({'rendered_template': rendered_template})




# save and generate PDF document
@app.route('/save', methods=['POST'])
def generate_pdf_route():
    content = request.form['content']
    pdf = HTML(string=content).write_pdf()
    return send_file(BytesIO(pdf), attachment_filename='document.pdf', mimetype='application/pdf')





# return  data into selector in html
def list_folders():
    folder_path = "Data/"
    folders = []
    for root, dirnames, filenames in os.walk(folder_path):
        for dirname in dirnames:
            if not dirname.startswith('.'):  # Ignore hidden directories
                folders.append(os.path.join(root, dirname))
    return folders
    files = []
    for root, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if not filename.startswith('.'):  # Ignore hidden files
                file = {}
                file["Key"] = os.path.join(root, filename)
                file["PresignedURL"] = url_for("static", filename=file["Key"])
                files.append(file)
    return files


# function for splitting path and generating subfolder path
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




@app.route('/get_folder_content', methods=['POST'])
def get_folder_content():
    global current_folder
    selected_folder = request.form['selected_folder']
    folder_path = f'Data/{selected_folder}'
    folder_content = get_files_recursive(folder_path)
    print(f"Selected folder: {selected_folder}")  # Print the selected folder in the terminal
    current_folder = selected_folder
    return {'folder_content': folder_content}





@app.route('/filemanager/')
@app.route('/filemanager/<path:subpath>')
def file_manager(subpath=None):
    if subpath:
        subpath = subpath.strip('/')  # remove trailing slashes
        dir_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
    else:
        dir_path = app.config['UPLOAD_FOLDER']
        subpath = ''

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
        files = request.files.getlist('files')
        if files:
            if subpath:
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
            else:
                save_path = app.config['UPLOAD_FOLDER']

            for file in files:
                if isinstance(file, FileStorage):
                    file_path = os.path.join(save_path, secure_filename(file.filename))
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)

            flash('Files uploaded successfully.')
            return redirect(url_for('file_manager', subpath=subpath))
    flash('Error uploading files.')
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

@app.route('/create_folder/', methods=['POST'])
@app.route('/create_folder/<path:subpath>', methods=['POST'])
def create_folder(subpath=None):
    folder_name = request.form['folder_name']
    if subpath:
        parent_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
    else:
        parent_path = app.config['UPLOAD_FOLDER']
    
    new_folder_path = os.path.join(parent_path, folder_name)
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        flash('Folder created successfully.')
    else:
        flash('Folder already exists.')

    return redirect(url_for('file_manager', subpath=subpath))

@app.route('/delete_folder/<path:folder_path>')
def delete_folder(folder_path):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        flash('Folder deleted successfully.')
    else:
        flash('Folder not found or not a directory.')

    return redirect(url_for('file_manager'))


@app.route('/Data/<path:file_path>')
def serve_file(file_path):
    data_folder_path = os.path.abspath('Data')
    return send_from_directory(data_folder_path, file_path)

#runn app as local on port 5000 , accesible on private and public AWS IP
app.run(host='0.0.0.0', port=5000)
