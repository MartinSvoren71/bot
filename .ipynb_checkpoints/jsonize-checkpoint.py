import os
import boto3
from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from main import api_kx

AWS_ACCESS_KEY_ID = 'AKIA5BVJA3S5MNPVO2MP'
AWS_SECRET_ACCESS_KEY = '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'
AWS_DEFAULT_REGION = 'eu-north-1'
BUCKET_NAME = 'knowledgevortex'


def initialize_ai(api_key_value):
    os.environ["OPENAI_API_KEY"] = api_key_value

def download_files_from_s3(bucket_name, directory_path):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=directory_path):
        if obj.key.endswith(".json"):
            bucket.download_file(obj.key, obj.key.split("/")[-1])

def upload_file_to_s3(file_path, bucket_name, object_key):
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, object_key).put(Body=open(file_path, "rb"))

def construct_index(directory_path, api_key, bucket_name):
    index_file = "index.json"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # Check if the index file already exists in the S3 bucket
    index_exists = False
    for obj in bucket.objects.filter(Prefix=f"{directory_path}/{index_file}"):
        if obj.key == f"{directory_path}/{index_file}":
            index_exists = True
            break

    if not index_exists:
        max_input_size = 4096
        num_outputs = 2000
        max_chunk_overlap = 20
        chunk_size_limit = 600

        os.environ["OPENAI_API_KEY"] = api_key
        openai.api_key = api_key

        # Download JSON files from the S3 bucket
        for obj in bucket.objects.filter(Prefix=directory_path):
            if obj.key.endswith(".json"):
                bucket.download_file(obj.key, obj.key.split("/")[-1])

        documents = SimpleDirectoryReader(directory_path).load_data()

        # Create a GPTSimpleVectorIndex with the downloaded documents
        index = GPTSimpleVectorIndex(
            documents, llm_predictor=None, prompt_helper=None
        )

        # Save the index to disk
        index.save_to_disk(index_file)

        # Upload the index file to the S3 bucket
        s3.Object(bucket_name, f"{directory_path}/{index_file}").put(Body=open(index_file, "rb"))

        # Remove the local index file and downloaded data
        os.remove(index_file)
        for obj in bucket.objects.filter(Prefix=directory_path):
            if obj.key.endswith(".json"):
                os.remove(obj.key.split("/")[-1])

    # Load the index from the S3 bucket
    bucket.download_file(f"{directory_path}/{index_file}", index_file)
    index = GPTSimpleVectorIndex.load_from_disk(index_file)
    os.remove(index_file)

    # Perform LLM prediction
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-curie-001", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    index.set_llm_predictor(llm_predictor)
    index.set_prompt_helper(prompt_helper)

    return index
