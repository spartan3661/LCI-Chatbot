
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings

from langchain_core.documents import Document
import pandas as pd

embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-3-small",
    model="text-embedding-3-small",
    azure_endpoint="",
    api_key="",
    api_version="2024-02-01"
)

"""
vector = embeddings.embed_query("This is a test.")
print(vector)

embeddings = HuggingFaceEmbeddings(
    model="BAAI/bge-base-en-v1.5"
)
"""


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


