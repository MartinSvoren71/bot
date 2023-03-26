from flask import Flask, request, render_template, redirect, url_for, flash, session
from ask_ai import initialize_ai, ask_ai
from ask_GPT import initialize_GPT, ask_GPT
from threading import Thread
from main import api_kx
from datetime import timedelta
import os
import json
import boto3
from botocore.exceptions import ClientError
aws_access_key_id = 'AKIA5BVJA3S5MNPVO2MP'
aws_secret_access_key = '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'
aws_default_region = 'eu-central-1'

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_default_region
)

app = Flask(__name__)
app.secret_key = "xxx007"
pdf_urla="https://knowledgevortex.s3.eu-north-1.amazonaws.com/s3/data/ChameleonDiscovery/Chameleon_Discovery_TPC_1313627_RevAC_press_covers.pdf"
pdf_url=pdf_urla

@app.route('/list_files')
def list_files():
    bucket_name = 'knowledgewortex'
    folder_path = 's3/data/'
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    except ClientError as e:
        return {'error': str(e)}
    
    files = [{'Key': item['Key'], 'Size': item['Size']} for item in response.get('Contents', [])]
    return {'files': files}


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
        return render_template("indexSplit.html", html=html, pdf_url=pdf_url)
    else:
        flash("Please log in first")
        return redirect(url_for("login"))
@app.route('/display', methods=['GET'])
def display():
    question = request.args.get('question')
    theme = request.args.get('theme')
    response = request.args.get('response')
    key = request.args.get('key')
    return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key, pdf_url=pdf_url)
@app.route('/log-content')
def log_content():
    file_path = os.path.join(os.getcwd(), 'log.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    return content
@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    theme = request.form['theme']
    key = "nnp"
    if key == "nnp":  # Check if the key is "xxx007"
        if theme == "general":
            response = ask_GPT(question)  # Pass the theme value
            return render_template('indexSplit.html', question=question, response=response, key=key, pdf_url=pdf_url)
        else:
            response = ask_ai(question, theme)  # Pass the theme value
            return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key, pdf_url=pdf_url)
    else:
        return render_template('bad_key.html', question=question, theme=theme)

t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
#

