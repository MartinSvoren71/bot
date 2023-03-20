import os
from threading import Thread
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from main import api_kx


api_k = api_kx

def initialize_ai(api_key):
    os.environ["*"] = api_key
    os.environ[api_k] = api_key


def construct_index(directory_path):
@ -15,7 +15,7 @@ def construct_index(directory_path):
    max_chunk_overlap = 20
    chunk_size_limit = 600

    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-curie-001", max_tokens=num_outputs, openai_api_key="*"))
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.7, model_name="davinci", max_tokens=num_outputs, openai_api_key=api_k))

    documents = SimpleDirectoryReader(directory_path).load_data()

@ -29,7 +29,46 @@ def construct_index(directory_path):


def ask_ai(question):
    os.environ["OPENAI_API_KEY"] = "*"
    os.environ["OPENAI_API_KEY"] = api_k
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    response = index.query(question, response_mode="compact")
    return response.response



import os
from threading import Thread
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI

api_k = *

def initialize_ai(api_key):
    os.environ[api_k] = api_key


def construct_index(directory_path, theme):
    max_input_size = 4096
    num_outputs = 2000
    max_chunk_overlap = 20
    chunk_size_limit = 600

    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.7, model_name="davinci", max_tokens=num_outputs, openai_api_key=api_k))
    
    documents = SimpleDirectoryReader(directory_path).load_data()

    if theme == "chameleon":
        index_file = "indexCH.json"
    elif theme == "compex":
        index_file = "indexCompex.json"
    else:
        index_file = "index.json"

    index = GPTSimpleVectorIndex.load_from_disk(index_file)

    return index


def ask_ai(question, theme):
    os.environ["OPENAI_API_KEY"] = api_k
    index = construct_index("directory_path", theme)
    response = index.query(question, response_mode="compact")
    return response.response