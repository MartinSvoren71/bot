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
import boto3

folder_name = 's3/'

AWS_ACCESS_KEY_ID = 'AKIA5BVJA3S5MNPVO2MP'
AWS_SECRET_ACCESS_KEY = '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'
AWS_DEFAULT_REGION = 'eu-north-1'
BUCKET_NAME = 'knowledgevortex'
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)



def initialize_ai(api_key):
    os.environ[api_k] = api_kx
#
def construct_index(directory_path):
    max_chunk_overlap = 20
    chunk_size_limit = 600
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.9, model_name="text-davinci-003", max_tokens=num_outputs, openai_api_key=api_k))
    documents = SimpleDirectoryReader(directory_path).load_data()
    os.environ["OPENAI_API_KEY"] = api_kx
    openai.api_key = api_kx

initialize_ai(api_k)

    
def ask_ai(question, theme):
    # Load the theme file names from the themes.json file
    with open('themes.json', 'r') as f:
        themes = json.load(f)

    # Get the file name for the current theme
    index_file = themes.get(theme, "indexChameleon.json")
    
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
        
   # return response.response

