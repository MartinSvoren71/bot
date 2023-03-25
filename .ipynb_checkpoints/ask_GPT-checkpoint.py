from flask import Flask, request, jsonify
import os
from threading import Thread
from langchain import OpenAI
import datetime
import openai
import json

api_k = "your_api_key_here"

def initialize_ai(api_key):
    os.environ["OPENAI_API_KEY"] = api_key
    openai.api_key = api_key

initialize_ai(api_k)

def ask_ai(question, theme):
    os.environ["OPENAI_API_KEY"] = api_k
    prompt = f"{theme}: {question}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.9,
    )

    answer = response.choices[0].text.strip()

    log_file = os.path.join(os.getcwd(), 'log.txt')

    # Read the existing data in the log file
    with open(log_file, "r") as f:
        existing_data = f.read()

    # Write the new data followed by the existing data
    with open(log_file, "w") as f:
        f.write(f"Time: {datetime.datetime.now()}\n")
        f.write(f"Theme: {theme}\n")
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {answer}\n")
        f.write("======================================================================================\n")
        f.write("                         Knowlege Vortex v1.1                                 \n")
        f.write("======================================================================================\n")
        f.write(existing_data)

    return answer
