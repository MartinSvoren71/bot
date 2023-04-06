import os
os.environ["OPENAI_API_KEY"] = 'YOUR_OPENAI_API_KEY'

from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader('datatest').load_data()
index = GPTSimpleVectorIndex.from_documents(documents)

# save to disk
index.save_to_disk('index.json')
# load from disk
index = GPTSimpleVectorIndex.load_from_disk('index.json')

index.query("<question_text>?")

