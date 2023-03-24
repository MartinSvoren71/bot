from flask import Flask, request, render_template, redirect, url_for, flash, session
from ask_ai import initialize_ai, ask_ai
from threading import Thread
from main import api_kx
from datetime import timedelta
import os

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
        return render_template("indexSplit.html")
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
    key = "nnp"
    question = request.form['question']
    theme = request.form['theme']
    key = request.form['key']  # Get the value of the key from the form
    if key == "nnp":  # Check if the key is "xxx007"
        response = ask_ai(question, theme)  # Pass the theme value
        return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return render_template('indexSplit.html', question=question, theme=theme)
t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port=5000)
#