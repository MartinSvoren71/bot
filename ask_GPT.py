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
    os.environ[api_k] = api_k
    openai.api_key = api_k


    
def ask_GPT(question, theme):
    # Load the theme file names from the themes.json file
    with open('themes.json', 'r') as f:
        themes = json.load(f)

    # Get the file name for the current theme
    index_file = themes.get(theme, "indexCH.json")
    
    os.environ["OPENAI_API_KEY"] = api_k
    index = GPTSimpleVectorIndex.load_from_disk(index_file)
    response = index.query(question, response_mode="compact")
    log_file = os.path.join(os.getcwd(), 'log.txt')
    
    # Read the existing data in the log file
    with open(log_file, "r") as f:
        existing_data = f.read()
    
    # Write the new data followed by the existing data
    with open(log_file, "w") as f:
        f.write(f"Time: {datetime.datetime.now()}\n")
        f.write(f"Theme: {theme}\n")
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {response.response}\n")
        f.write("======================================================================================\n")
        f.write("                         Knowlege Vortex v1.1                                 \n")
        f.write("======================================================================================\n")
        f.write(existing_data)
        
    return response.response

