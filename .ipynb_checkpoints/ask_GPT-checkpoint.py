from flask import Flask, request, jsonify
import os
import openai
from threading import Thread
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from main import api_kx
import datetime
api_k = api_kx
import json

def initialize_GPT(api_key):
    os.environ["OPENAI_API_KEY"] = api_kx
    openai.api_key = api_kx

initialize_GPT(api_k)

def ask_GPT(question):
    os.environ["OPENAI_API_KEY"] = api_kx
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=1550,
        n=1,
        stop=None,
        temperature=0.6,
    )

    answer = response.choices[0].text.strip()

    log_file = os.path.join(os.getcwd(), 'log.txt')
    
    # Read the existing data in the log file
    with open(log_file, "r") as f:
        existing_data = f.read()
    
    # Write the new data followed by the existing data
    with open(log_file, "w") as f:
        f.write(f"Time: {datetime.datetime.now()}\n")
        f.write(f"Question: {question}\n")
        f.write(f"Operator: {answer}\n")  # Replace response.answer with answer
        f.write("======================================================================================\n")
        f.write("                         Knowlege Vortex v1.5                                 \n")
        f.write("======================================================================================\n")
        f.write(existing_data)
        
    #return answer
