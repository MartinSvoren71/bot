#!pip install llama-index
#!pip install langchain
#   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
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
import sys
import os
from IPython.display import Markdown, display


def construct_index(directory_path):
    max_input_size = 4096
    num_outputs = 2000
    max_chunk_overlap = 20
    chunk_size_limit = 600

    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-curie-001", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    documents = SimpleDirectoryReader(directory_path).load_data()

    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )

    index.save_to_disk('index.json')

    return index


def ask_ai():
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    while True:
        query = input("What do you want to ask? ")
        response = index.query(query, response_mode="compact")
        print(f"Response: {response.response}\n")


def main():
    os.environ["OPENAI_API_KEY"] = input("Paste your OpenAI key here and hit enter:")

    data_directory = "context_data/data"
    index_file = "index.json"

    if not os.path.exists(index_file):
        print(f"Constructing index from data in {data_directory}...")
        construct_index(data_directory)
        print("Index constructed and saved to disk.")

    print("\nYou can now ask questions. Type 'exit' to quit.\n")
    while True:
        question = input("What do you want to ask? ")
        if question.strip().lower() == "exit":
            break
        else:
            ask_ai()


if __name__ == "__main__":
    main()
