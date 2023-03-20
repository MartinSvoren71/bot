import os
import sys
from flask import Flask, request, render_template, redirect, url_for
from ask_ai import initialize_ai, ask_ai
from threading import Thread
from main import api_kx

app = Flask(__name__)

 def create_app(api_key):
    app = Flask(__name__)
    app.config["API_KEY"] = api_key

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/ask', methods=['POST'])
    def ask_question():
        question = request.form['question']
        option = request.form['option']

        if question.strip().lower() == 'exit':
            return redirect(url_for('home'))
        else:
            if option == '1':
                index_file = 'index.json'
            elif option == '2':
                index_file = 'indexCH.json'
            else:
                # Default to option 1
                index_file = 'index.json'

            # Construct index if it doesn't exist
            if not os.path.exists(index_file):
                construct_index(directory_path)

            # Load index and get response
            index = GPTSimpleVectorIndex.load_from_disk(index_file)
            response = ask_ai(question, index)
            return render_template('response.html', question=question, response=response)

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
    

   
