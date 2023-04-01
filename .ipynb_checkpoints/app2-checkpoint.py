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
import boto3
from PyPDF4 import PdfFileReader, PdfFileWriter
import io 
from io import BytesIO
folders = "Data/Coherent/"

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
        folder_path = "{folders}"   # those are used for listing pdf files   folders
        files = []
        folders = list_folders_route()

        for root, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                if not filename.startswith('.'):  # Ignore hidden files
                    file = {}
                    file["Key"] = os.path.join(root, filename)
                    file["PresignedURL"] = url_for("static", filename=file["Key"])
                    files.append(file)
            #for dirname in dirnames:
                #if not dirname.startswith('.'):  # Ignore hidden directories
                   # folders.append(os.path.join(root, dirname))
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
    contents = s3_client.list_objects(Bucket=BUCKET_NAME, Prefix=(folder_name))
    files = contents['Contents']
    for file in files:
        file['PresignedURL'] = generate_presigned_url(BUCKET_NAME, file['Key'])
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
            file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=filepath)
            pdf_file = io.BytesIO(file_obj['Body'].read())
            pdf_reader = PdfFileReader(pdf_file)
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
    #folder_name = 's3/data/coherent_chameleon/'

    if request.method == 'POST':
        keyword = request.form['keyword']
        contents = s3_client.list_objects(Bucket=BUCKET_NAME, Prefix=folder_name)
        file_paths = [content['Key'] for content in contents['Contents'] if content['Key'].lower().endswith('.pdf')]
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





# return  data into selector in html
@app.route('/list_folders', methods=['POST'])
def list_folders_route():
    folder_path = "Data/"
    folders = []
    for root, dirnames, filenames in os.walk(folder_path):
        for dirname in dirnames:
            if not dirname.startswith('.'):  # Ignore hidden directories
                folders.append(os.path.join(root, dirname))
    return folders

@app.route('/list_files')
def list_files(folders):
    files = []
    for root, dirnames, filenames in os.walk(folders):
        for filename in filenames:
            if not filename.startswith('.'):  # Ignore hidden files
                file = {}
                file["Key"] = os.path.join(root, filename)
                file["PresignedURL"] = url_for("static", filename=file["Key"])
                files.append(file)
    return files

t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
