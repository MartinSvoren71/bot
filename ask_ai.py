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
        "kymera": "indexKymera.json"

    }.get(theme, "indexCH.json")  # Default to "indexCH.json" if the theme value is not recognized
    index = GPTSimpleVectorIndex.load_from_disk(index_file)
    response = index.query(question, )
    return response.response



