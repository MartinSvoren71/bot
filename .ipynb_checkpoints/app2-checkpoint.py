from flask import Flask, request, render_template, redirect, url_for, flash, session
from ask_ai import initialize_ai, ask_ai
from ask_GPT import initialize_GPT, ask_GPT
from threading import Thread
from main import api_kx
from datetime import timedelta
import os
import json

app = Flask(__name__)
app.secret_key = "xxx007"

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
        return render_template("indexSplit.html", html=html)
    else:
        flash("Please log in first")
        return redirect(url_for("login"))


@app.route('/display', methods=['GET'])
def display():
    question = request.args.get('question')
    theme = request.args.get('theme')
    response = request.args.get('response')
    key = request.args.get('key')
    return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)

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
        if theme == "general" :
            response = ask_GPT(question)  # Pass the theme value
            return render_template('indexSplit.html', question=question, response=response, key=key)
        else :
            response = ask_ai(question, theme)  # Pass the theme value
            return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return render_template('bad_key.html', question=question, theme=theme)
t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
#



@app.route('/ask2', methods=['POST'])
def ask2():
    question = request.form['question']
    theme = request.form['theme']
    key = "nnp"
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_ai(question, theme)  # Pass the theme value
        return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return render_template('bad_key.html', question=question, theme=theme)
t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
#