import boto3
import json
import os

from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from IPython.display import Markdown, display
data_directory = "/s3/data/"


def get_folders(s3_client, bucket_name):
    result = s3_client.list_objects(Bucket=bucket_name, Delimiter='/')
    folders = [item['Prefix'] for item in result.get('CommonPrefixes', [])]
    return folders


def generate_json_from_pdf(s3_client, bucket_name, folder_name):
    # Your logic to generate JSON from PDF files within the folder should be here
    # ...

    json_content = {}  # Replace with the actual JSON content you generate from PDF files
    json_filename = f"{folder_name}.json"

    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{folder_name}{json_filename}",
        Body=json.dumps(json_content),
        ContentType="application/json"
    )


def check_and_generate_json(s3_client, bucket_name, folder_name):
    objects_in_folder = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    json_filename = f"{folder_name}.json"

    json_exists = False
    for obj in objects_in_folder.get("Contents", []):
        if obj["Key"].endswith(json_filename):
            json_exists = True
            break

    if not json_exists:
        generate_json_from_pdf(s3_client, bucket_name, folder_name)


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

    folder_name = 's3/'
    AWS_ACCESS_KEY_ID = 'AKIA5BVJA3S5MNPVO2MP'
    AWS_SECRET_ACCESS_KEY = 'QspohE+8VYcwJzA18cvfQJQZFst2q+WEgMtqvC1A'
    AWS_DEFAULT_REGION = 'eu-north-1'
    BUCKET_NAME = 'knowledgevortex'

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

    folders = get_folders(s3_client, BUCKET_NAME)
