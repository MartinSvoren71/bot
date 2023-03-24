from flask import Flask, request, render_template, redirect, url_for, jsonify
from ask_ai import initialize_ai, ask_ai
from threading import Thread
from main import api_kx
import os
app = Flask(__name__)

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

@app.route('/')
def home():
    file_path = os.path.join(os.getcwd(), 'log.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    return render_template('index.html', content=content)
 if question.strip().lower() == 'exit':
        return redirect(url_for('home'))
    elif key == "xxx007":  # Check if the key is "xxx007"
        response = ask_ai(question, theme)  # Pass the theme value 
            return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)

       # return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return render_template('badkey.html')


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    theme = request.form['theme']
    key = request.form['key']  # Get the value of the key from the form
    #response = ask_ai(question, theme)  # Pass the theme value

    if question.strip().lower() == 'exit':
        return redirect(url_for('home'))
    elif key == "xxx007":  # Check if the key is "xxx007"
        response = ask_ai(question, theme)  # Pass the theme value      
       # return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return render_template('badkey.html')


t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port='5000')



