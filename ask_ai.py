from flask import Flask, request, jsonify
import os
import openai
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from main import api_kx
import datetime
import json
api_k=api_kx
from llama_index import LLMPredictor, GPTSimpleVectorIndex, PromptHelper, ServiceContext
from langchain import OpenAI
def initialize_ai(api_key):
    os.environ[api_k] = api_kx
    
initialize_ai(api_k)


def ask_ai(question, current_folder):
    # Preselected folder and index.json file
    folder_path = f'Data/{current_folder}'
    index_file = f"{folder_path}/index.json"
    data_directory = folder_path

    if not os.path.exists(index_file):
        print(f"Constructing index from data in {data_directory}...")
        index = construct_index(data_directory)  # Save the returned index in a variable
        print("Index constructed and saved to disk.")

    index_file = f"{folder_path}/index.json"
    os.environ["OPENAI_API_KEY"] = api_k
    #documents = SimpleDirectoryReader(folder_path).load_data('index.json')
    #index = GPTSimpleVectorIndex.from_documents(documents)
    index = GPTSimpleVectorIndex.load_from_disk(index_file)
    response = index.query(question)  #
    print(response)
    log_file = os.path.join(os.getcwd(), 'log.txt')

    
    # Read the existing data in the log file
    with open(log_file, "r") as f:
        existing_data = f.read()

    # Write the new data followed by the existing data
    with open(log_file, "w") as f:
        f.write(f"Time: {datetime.datetime.now()}\n\n")
        f.write(f"Folder: {folder_path}\n\n")
        f.write(f"Question: {question}\n\n")
        f.write(f"Operator: {response.response}\n\n")
        f.write("======================================================================================\n")
        f.write("                         Knowlege Vortex v1.5                                 \n")
        f.write("=======================================================================================\n\n")
        f.write(existing_data)

    # return response.response


def construct_index(current_folder):

    folder_path = f'Data/{current_folder}'
    index_file = f"{folder_path}/index.json"

     # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003"))

# define prompt helper
# set maximum input size
    max_input_size = 4096
# set number of output tokens
    num_output = 256
# set maximum chunk overlap
    max_chunk_overlap = 20
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    
    documents = SimpleDirectoryReader(folder_path).load_data()
    index = GPTSimpleVectorIndex.from_documents(documents)
    #index.save_to_disk('index.json') # Save the index with the new version
    index.save_to_disk(index_file)  # Save the index to the index_file

    return index




  