from flask import Flask, request, render_template, redirect, url_for, flash, session
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
from PyPDF4 import PdfFileReader



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
        contents = s3_client.list_objects(Bucket=BUCKET_NAME)
        files = contents['Contents']
        for file in files:
            file['PresignedURL'] = generate_presigned_url(BUCKET_NAME, file['Key'])
        return render_template("indexSplit.html", html=html, files=files)
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

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    theme = request.form['theme']
    model = request.form['model']
    key = "nnp"
    contents = s3_client.list_objects(Bucket=BUCKET_NAME)
    files = contents['Contents']
    for file in files:
        file['PresignedURL'] = generate_presigned_url(BUCKET_NAME, file['Key'])
    if key == "nnp":  # Check if the key is "xxx007"
        if theme == "general" :
            response = ask_GPT(question, model, theme)  # Pass the theme value
            return render_template("indexSplit.html", question=question, response=response, key=key, files=files, model=model, theme=theme)
        else :
            response = ask_ai(question, theme, model)  # Pass the theme value
            return render_template("indexSplit.html", question=question, theme=theme, response=response, key=key, files=files, model=model)
    else:
        return render_template('bad_key.html', question=question, theme=theme)
    
    
def search_pdf_files(keyword, directory):
    results = {}
    encrypted_files = []  # List to store encrypted files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pdf'):
                filepath = os.path.join(root[len(directory) - 1:], file)
                try:
                    with open(filepath, 'rb') as pdf_file:
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


@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = {}
    encrypted_files = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        directory = "/"  # Replace with the specific directory you want to search
        search_results, encrypted_files = search_pdf_files(keyword, directory)
    return render_template('index.html', results=search_results, encrypted_files=encrypted_files)

    
    
    
t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
