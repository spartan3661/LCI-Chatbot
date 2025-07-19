from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
import pandas as pd
import os

load_dotenv() 

embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-3-small",
    model="text-embedding-3-small",
    azure_endpoint=os.getenv("OPENAI_EMBEDDINGS_ENDPOINT"),
    api_key=os.getenv("OPENAI_API"),
    api_version="2024-02-01"
)

df = pd.read_csv("wordpress_posts.csv")

documents = []
ids = []
for i, row in df.iterrows():
    document = Document(
        page_content=row["title"] + " " + row["content"],
        metadata={"date": row["date"], "id": str(i)}
    )
    documents.append(document)
    ids.append(str(i))

vector_store = Chroma(
    collection_name="articles",
    persist_directory="./chroma_langchain_db",
    embedding_function=embeddings
)

vector_store.add_documents(documents, ids=ids)


