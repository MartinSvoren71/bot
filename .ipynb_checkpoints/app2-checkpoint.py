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


current_folder = 'Data/'

folder_name = 's3/'
app = Flask(__name__, static_folder='/')
app.secret_key = "xxx007"
AWS_ACCESS_KEY_ID = 'AKIA5BVJA3S5MNPVO2MP'
AWS_SECRET_ACCESS_KEY = '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'
AWS_DEFAULT_REGION = 'eu-north-1'
BUCKET_NAME = 'knowledgevortex'
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["key"]
        if password == app.secret_key :
            session["logged_in"] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=1)
            return redirect(url_for("index"))
        else:
            flash("Bad key provided")
            return redirect(url_for("bad_key"))
    return render_template("login.html")
@app.route("/bad_key")



def bad_key():
    return render_template("badkey.html")



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




@app.route("/indexSplit", methods=["GET", "POST"])
def index():
    if "logged_in" in session:
        with open('themes.json', 'r') as f:
            themes = json.load(f)
        options = ''.join([f'<option value="{theme}">{theme_name}</option>' for theme, theme_name in themes.items()])
        html = f'''
        <select name="theme" id="theme" onchange="saveTheme()">
            {options}
        </select>
        '''
        data_folders = get_subfolders_recursive('Data/')
        folder_path = "Data/Coherent/Chameleon/"   # those are used for listing pdf files 
        files = list_files_and_urls(folder_path)
        folders = list_folders()

            #for dirname in dirnames:
                #if not dirname.startswith('.'):  # Ignore hidden directories
                   # folders.append(os.path.join(root, dirname))
        return render_template("indexSplit.html", html=html, folders=data_folders, files=files, results={})

    else:
        flash("Please log in first")
        return redirect(url_for("login"))

    
    
    

    
    
@app.route('/log-content')
def log_content():
    file_path = os.path.join(os.getcwd(), 'log.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    return content
def generate_presigned_url(bucket, key, expiration=3600):
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return None
    return response




@app.route('/ask_gpt', methods=['POST'])
def ask_GPT_route():
    key = "nnp"

    question = request.form['question']
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_GPT(question)  # Pass the theme value
        #return jsonify({"question": question, "response": response})
            #return render_template('indexSplit.html', question=question, response=response, key=key, files=files)
    else:
        return render_template('bad_key.html')
    
    
    
    
    
@app.route('/ask_lib', methods=['POST'])
def ask_LIB_route():
    question = request.form['question']
    model = "text-davinci-003"
    key = "nnp"
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_ai(question, current_folder)  # Pass the theme value
        #return jsonify({"question": question, "response": response})
            #return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key, files=files)
    else:
        return render_template('bad_key.html')
    


def process_pdf_file(filepath, keyword, pattern):
    result = []
    try:
        with open(filepath, 'rb') as f:
            pdf_reader = PdfFileReader(f)
            if pdf_reader.isEncrypted:
                return filepath, None, True
            for page_num in range(pdf_reader.getNumPages()):
                text = pdf_reader.getPage(page_num).extractText()
                matches = pattern.findall(text)
                if matches:
                    result.extend([(page_num, match) for match in matches])
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return filepath, None, False
    return filepath, result, False




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





app.run(host='0.0.0.0', port=5000)
