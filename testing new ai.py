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
        index.save_to_disk(index_file)  # Save the index to the index_file
        print("Index constructed and saved to disk.")

    index_file = f"{folder_path}/index.json"
    os.environ["OPENAI_API_KEY"] = api_k
    documents = SimpleDirectoryReader(folder_path).load_data()
    #index = GPTSimpleVectorIndex.from_documents(documents)
    index = GPTSimpleVectorIndex.load_from_disk(folder_path)
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
    os.environ["OPENAI_API_KEY"] = api_kx
    openai.api_key = api_kx
    
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

    index = GPTSimpleVectorIndex.from_documents(
    documents, service_context=service_context
)
    index.save_to_disk('index.json') # Save the index with the new version
    return index




    



from llama_index import SimpleDirectoryReader

documents = SimpleDirectoryReader('data').load_data()

from llama_index.node_parser import SimpleNodeParser

parser = SimpleNodeParser()

nodes = parser.get_nodes_from_documents(documents)

from llama_index import GPTSimpleVectorIndex

index = GPTSimpleVectorIndex.from_documents(documents)

from llama_index import LLMPredictor, GPTSimpleVectorIndex, PromptHelper, ServiceContext
from langchain import OpenAI

...

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

index = GPTSimpleVectorIndex.from_documents(
    documents, service_context=service_context
)
# save to disk
index.save_to_disk('index.json')
# load from disk
index = GPTSimpleVectorIndex.load_from_disk('index.json')

response = index.query("What did the author do growing up?")
print(response)

response = index.query("<query_str>")

# get response
# response.response
str(response)

# get sources
response.source_nodes
# formatted sources
response.get_formatted_sources()