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

def ask_GPT(question, model, theme):
    os.environ["OPENAI_API_KEY"] = api_kx
    if model == "gpt-3.5-turbo":
        response = openai.ChatCompletion.create(
        engine=model,
        prompt=question,
        max_tokens=1000,
        n=1,
   # stop=["\n", "Conclusion:"],
        temperature=0.7,
        )
    else:
        response = openai.Completion.create(
            engine=model,
            prompt=question,
            max_tokens=1000,
            n=1,
            temperature=0.7,
        )
    return response
    

    answer = response.choices[0].text.strip()

    log_file = os.path.join(os.getcwd(), 'log.txt')
    
    # Read the existing data in the log file
    with open(log_file, "r") as f:
        existing_data = f.read()
    
    # Write the new data followed by the existing data
    with open(log_file, "w") as f:
        f.write(f"Time: {datetime.datetime.now()}\n")
        f.write(f"Theme: {theme}\n")
        f.write(f"AI_Model: {model}\n")
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {answer}\n")  # Replace response.answer with answer
        f.write("======================================================================================\n")
        f.write("                         Knowlege Vortex v1.1                                 \n")
        f.write("======================================================================================\n")
        f.write(existing_data)
        
    return answer
