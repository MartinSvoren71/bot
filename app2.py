from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_file
from ask_ai import initialize_ai, ask_ai
from ask_GPT import initialize_GPT, ask_GPT
from threading import Thread
from main import api_kx
from datetime import timedelta
import os
import re
import json
import subprocess
from PyPDF4 import PdfFileReader, PdfFileWriter
import io 
from io import BytesIO
import boto3
import shutil
from pathlib import Path
from botocore.exceptions import ClientError


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




def sync_s3_to_local(s3_folder, local_folder):
    # Set the S3 bucket and folder names
    bucket_name = 'knowledgevortex'

    # Create an S3 client
   

    # Get the list of files in the S3 folder
    s3_files = []
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder)
        s3_files = [content['Key'] for content in response['Contents']]
    except ClientError as e:
        print("Error listing S3 folder:", s3_folder, e)
        return

    # Sync the S3 folder with the local folder
    for file_path in s3_files:
        file_name = os.path.basename(file_path)
        # Create the subdirectory structure in the local folder
        sub_dir = os.path.dirname(file_path).replace(s3_folder, "")
        local_sub_dir = os.path.join(local_folder, sub_dir)
        os.makedirs(local_sub_dir, exist_ok=True)
        # Download the file to the local folder
        local_file_path = os.path.join(local_folder, file_path.replace(s3_folder, ""))
        try:
            s3_client.download_file(bucket_name, file_path, local_file_path)
            print("Downloaded file:", local_file_path)
        except ClientError as e:
            print("Error downloading file:", local_file_path, e)

sync_s3_to_local('s3/data/', '/s3/data/')





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

@app.route("/indexSplit", methods=["GET", "POST"])
def index():
    if "logged_in" in session:
        local_folder = 's3/data/'
          
        folders = [folder for folder in os.listdir(local_folder) if os.path.isdir(os.path.join(local_folder, folder))]
        # Load the themes from the themes.json file
        with open('themes.json', 'r') as f:
            themes = json.load(f)
        # Generate the <option> elements dynamically
        options = ''.join([f'<option value="{theme}">{theme_name}</option>' for theme, theme_name in themes.items()])
        # Render the HTML with the dynamic <option> elements
        html = f'''
        <select name="theme" id="theme" onchange="saveTheme()">
            {options}
        </select>
        '''
        
        files = [file for file in os.listdir(local_folder) if os.path.isfile(os.path.join(local_folder, file))]
        
        return render_template("indexSplit.html", html=html, folders=folders, files=files, results={})

    else:
        flash("Please log in first")
        return redirect(url_for("login"))
    
    
@app.route('/log-content')
def log_content():
    file_path = os.path.join(os.getcwd(), 'log.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def generate_local_file_path(folder, filename):
    try:
        file_path = os.path.join(folder, filename)
    except Exception as e:
        print(e)
        return None
    return file_path

@app.route('/ask_gpt', methods=['POST'])
def ask_GPT_route():
    question = request.form['question']
    theme = request.form['theme']
    model = request.form['model']
    key = "nnp"
    contents = s3_client.list_objects(Bucket=BUCKET_NAME, Prefix=(folder_name))
    files = contents['Contents']
    for file in files:
        file['PresignedURL'] = generate_presigned_url(BUCKET_NAME, file['Key'])
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_GPT(question)  # Pass the theme value
        #return jsonify({"question": question, "response": response})
            #return render_template('indexSplit.html', question=question, response=response, key=key, files=files)
    else:
        return render_template('bad_key.html', question=question, theme=theme)
    
@app.route('/ask_lib', methods=['POST'])
def ask_LIB_route():
    question = request.form['question']
    theme = request.form['theme']
    model = "text-davinci-003"
    key = "nnp"
    local_folder = 's3/data/'

    files = [os.path.join(local_folder, file) for file in os.listdir(local_folder)]

    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_ai(question, theme)  # Pass the theme value
        #return jsonify({"question": question, "response": response})
            #return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key, files=files)
    else:
        return render_template('bad_key.html', question=question, theme=theme)
    
def search_pdf_files(keyword, file_paths):
    results = {}
    encrypted_files = []  # List to store encrypted files
    for filepath in file_paths:
        try:
            with open(filepath, 'rb') as file_obj:
                pdf_reader = PdfFileReader(file_obj)
                if pdf_reader.isEncrypted:
                    print(f"Skipping encrypted file: {filepath}")
                    encrypted_files.append(filepath)  # Add the encrypted file to the list
                    continue
                for page_num in range(pdf_reader.getNumPages()):
                    text = pdf_reader.getPage(page_num).extractText()
                    pattern = re.compile(r'(?<=\.)([^.]*\b{}\b[^.]*(?:\.[^.]*){{0,1}})'.format(keyword))
                    matches = pattern.findall(text)
                    if matches:
                        if filepath not in results:
                            results[filepath] = []
                        results[filepath].extend([(page_num, match) for match in matches])
        except Exception as e:
            print(f"Error processing {filepath}: {str(e)}")
    return results, encrypted_files

@app.route('/search_pdf_files', methods=['POST'])
def search_files():
    search_results = {}
    encrypted_files = []
    local_folder = 's3/data/'

    if request.method == 'POST':
        keyword = request.form['keyword']
        file_paths = [os.path.join(local_folder, file) for file in os.listdir(local_folder) if file.lower().endswith('.pdf')]
        search_results, encrypted_files = search_pdf_files(keyword, file_paths)
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

def list_folders(local_folder):
    try:
        folders = [folder for folder in os.listdir(local_folder) if os.path.isdir(os.path.join(local_folder, folder))]
    except Exception as e:
        print(e)
        return []
    return folders


t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
