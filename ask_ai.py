import os
from threading import Thread
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from main import api_kx


api_k = api_kx

def initialize_ai(api_key):
    os.environ[api_k] = api_key


def construct_index(directory_path):
    max_chunk_overlap = 20
    chunk_size_limit = 600


    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.7, model_name="davinci", max_tokens=num_outputs, openai_api_key=api_k))

    documents = SimpleDirectoryReader(directory_path).load_data()




def ask_ai(question):
    os.environ["OPENAI_API_KEY"] = api_k
    index = GPTSimpleVectorIndex.load_from_disk('indexCompex.json')
    response = index.query(question, response_mode="compact")
    return response.response


