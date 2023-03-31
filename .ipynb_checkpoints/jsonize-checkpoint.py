from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
import sys
import os
import boto3
from IPython.display import Markdown, display
from main import api_kx
api_key=api_kx

folder_name = 's3/data/coherent_chameleon'
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

def construct_index(directory_path, api_key, bucket_name):
    max_input_size = 4096
    num_outputs = 2000
    max_chunk_overlap = 20
    chunk_size_limit = 600

    os.environ["OPENAI_API_KEY"] = api_key
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-curie-001", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    documents = SimpleDirectoryReader(directory_path).load_data()
    for doc in documents:
        s3_object = bucket.Object(f"{directory_path}/{doc}")
        s3_object.put(Body=doc)

    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )

    index.save_to_disk('index.json')

    return index


def check_and_construct_index(directory_path, api_key, bucket_name):
    index_file = "index.json"

    if not os.path.exists(index_file):
        print(f"Constructing index from data in {directory_path}...")
        index = construct_index(directory_path, api_key, bucket_name)
        print("Index constructed and saved to disk.")
    else:
        index = GPTSimpleVectorIndex.load_from_disk('index.json')

    return index


def main():
    api_key = input("Paste your OpenAI key here and hit enter:")
    bucket_name = 'knowledgevortex'

    data_directory = "context_data/data"
    index_file = "index.json"

    index = check_and_construct_index(data_directory, api_key, bucket_name)

    print("\nYou can now ask questions. Type 'exit' to quit.\n")
    while True:
        question = input("What do you want to ask? ")
        if question.strip().lower() == "exit":
            break
        else:
            response = index.query(question, response_mode="compact")
            print(f"Response: {response.response}\n")


if __name__ == "__main__":
    main()
