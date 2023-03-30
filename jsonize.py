import boto3
import os
import tempfile
import shutil
from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
import logging
from main import api_kx

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler('jsonoze.txt', mode='w'),
                              logging.StreamHandler()])

def initialize_GPT(api_key):
    os.environ["OPENAI_API_KEY"] = api_kx
    openai.api_key = api_kx

initialize_GPT(api_kx)

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

def download_folder(s3_client, bucket, prefix, local_dir):
    paginator = s3_client.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for content in result.get('Contents', []):
            s3_path = content['Key']
            local_path = os.path.join(local_dir, s3_path[len(prefix):])
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3_client.download_file(bucket, s3_path, local_path)

def upload_file(s3_client, bucket, s3_path, local_path):
    s3_client.upload_file(local_path, bucket, s3_path)

def check_and_generate_json(s3_client, bucket_name, folder):
    paginator = s3_client.get_paginator('list_objects_v2')
    result = paginator.paginate(Bucket=bucket_name, Prefix=folder)

    json_exists = False
    for page in result:
        for obj in page['Contents']:
            if obj['Key'].endswith('.json'):
                json_exists = True
                break
        if json_exists:
            break

    if not json_exists:
        logging.debug(f"JSON file not found in {folder}. Generating JSON file.")
        # Download the folder, generate JSON file using construct_index function, and upload it back to S3
        # Code to download folder from S3, generate JSON and upload
    else:
        logging.debug(f"JSON file found in {folder}.")

    if not json_exists:
        logging.debug(f"JSON file not found in {folder}. Generating JSON file.")

        with tempfile.TemporaryDirectory() as tempdir:
            local_folder = os.path.join(tempdir, folder)
            download_folder(s3_client, bucket_name, folder, local_folder)
            construct_index(local_folder)
            json_file_path = os.path.join(local_folder, "index.json")
            s3_json_file_path = os.path.join(folder, "index.json")
            upload_file(s3_client, bucket_name, s3_json_file_path, json_file_path)

        logging.debug(f"JSON file generated and uploaded to {folder}.")
    else:
        logging.debug(f"JSON file found in {folder}.")

def main():
    folder_name = 's3/data/'
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

    # List all directories in the specified folder
    paginator = s3_client.get_paginator('list_objects_v2')
    result = paginator.paginate(Bucket=BUCKET_NAME, Prefix=folder_name, Delimiter='/')

    for prefix in result.search('CommonPrefixes'):
        folder = prefix.get('Prefix')
        logging.debug(f"Checking folder: {folder}")
        check_and_generate_json(s3_client, BUCKET_NAME, folder)


if __name__ == "__main__":
    main()













