from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()  # Make sure .env is loaded

# Create the embedding client
embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-3-small",
    model="text-embedding-3-small",
    azure_endpoint=os.getenv("openai-embeddings-endpoint"),
    api_key=os.getenv("openai-embeddings"),
    api_version="2024-02-01"
)

# Test string
texts = ["Hello world!"]

# Try embedding
try:
    result = embeddings.embed_documents(texts)
    print("✅ Embedding successful!")
    print("Embedding vector:", result[0][:10], "...")  # Show first 10 dimensions
except Exception as e:
    print("❌ Embedding failed:")
    print(e)
