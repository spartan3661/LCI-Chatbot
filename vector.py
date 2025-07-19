from langchain_chroma import Chroma
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
import os

'''
embeddings = HuggingFaceEmbeddings(
    model="BAAI/bge-base-en-v1.5"
)
'''

embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-3-small", 
    model="text-embedding-3-small",
    azure_endpoint=os.getenv("OPENAI_EMBEDDINGS_ENDPOINT"),
    api_key=os.getenv("OPENAI_API"),
    api_version="2024-02-01"
)

vector_store = Chroma(
    collection_name="articles",
    persist_directory="./chroma_langchain_db",
    embedding_function=embeddings
)

retriever = vector_store.as_retriever(search_kwargs={"k": 5})
