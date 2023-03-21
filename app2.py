from flask import Flask, request, render_template, redirect, url_for
from ask_ai import initialize_ai, ask_ai
from threading import Thread
from main import api_kx
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form['question']
    theme = request.form['theme']
    if question.strip().lower() == 'exit':
        return redirect(url_for('home'))
    else:
        response = ask_ai(question, theme)  # Pass the theme value
        return render_template('response.html', question=question, theme=theme, response=response)
    t = Thread(target=initialize_ai)
    t.start()
    app.run(host='0.0.0.0', port='5000')    
  #  pass  # added to avoid indentation error
if __name__ == '__main__':
    openai_api_key = api_kx or (len(sys.argv) > 1 and sys.argv[1])
    if not openai_api_key:
        print("Error: No OpenAI API key provided. Set the OPENAI_API_KEY environment variable or pass the key as a command-line argument.")
        sys.exit(1)
    t = Thread(target=initialize_ai, args=(openai_api_key,))
    t.start()
    app.run(host='0.0.0.0', port='5000')
    
