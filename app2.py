from flask import Flask, request, render_template, redirect, url_for
from ask_ai import initialize_ai, ask_ai
from threading import Thread
from main import api_kx

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('indexSplit.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    theme = request.form['theme']
    key = request.form['key']  # Get the value of the key from the form

    if question.strip().lower() == 'exit':
        return redirect(url_for('home'))
    elif key == "xxx007":  # Check if the key is "xxx007"
        response = ask_ai(question, theme)  # Pass the theme value     
        with open('index.txt', 'r') as file:
            content = file.read()
        return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return render_template('badkey.html')


t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port='5000')
