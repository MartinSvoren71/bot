from flask import Flask, request, jsonify
import os
from threading import Thread
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from main import api_kx
import datetime
api_k = api_kx

def initialize_ai(api_key):
    os.environ[api_k] = api_key
#
def construct_index(directory_path):
    max_chunk_overlap = 20
    chunk_size_limit = 600
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.9, model_name="gpt-3.5-turbo", max_tokens=num_outputs, openai_api_key=api_k))
    documents = SimpleDirectoryReader(directory_path).load_data()

def ask_ai(question, theme):
    os.environ["OPENAI_API_KEY"] = api_k
    index_file = {
        "chameleon": "indexChameleon.json",
        "compex": "indexCompex.json",
        "chameleondiscovery": "indexChameleonDiscovery.json",
        "innova": "indexInnova.json",
        "powerline": "indexPowerLine.json",
        "newton": "indexNewton.json",
        "univet": "indexUnivet.json",
        "kymera": "indexKymera.json",
        "zygomx": "indexZygoMX.json"
    }.get(theme, "indexCH.json")
    index = GPTSimpleVectorIndex.load_from_disk(index_file)
    response = index.query(question, response_mode="compact")
    log_file = os.path.join(os.getcwd(), 'log.txt')
    
    # Read the existing data in the log file
    with open(log_file, "r") as f:
        existing_data = f.read()
    
    # Write the new data followed by the existing data
    with open(log_file, "w") as f:
        f.write(f"Time: {datetime.datetime.now()}\n")
    f.write(f"<span class='theme'>Theme: {theme}</span>\n")
    f.write(f"<span class='question'>Question: {question}</span>\n")
    f.write(f"<span class='response'>Answer: {response.response}</span>\n")
    f.write("======================================================================================\n")
    f.write(" ========OPTIXS==============OPTIXS=============OPTIXS=============OPTIXS=============\n")
    f.write("======================================================================================\n")
    f.write(existing_data)        
    return response.response

