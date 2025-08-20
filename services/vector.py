from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings
import os



embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-3-small", 
    model="text-embedding-3-small",
    azure_endpoint=os.getenv("OPENAI_EMBEDDINGS_ENDPOINT"),
    api_key=os.getenv("OPENAI_EMBEDDINGS_API"),
    api_version="2024-02-01"
)


client = QdrantClient(host=os.environ.get("QDRANT_HOST"), 
                      port=int(os.environ.get("QDRANT_PORT", 6333)),
                      api_key=os.environ.get("QDRANT_API"),
                      https=False)


vector_store = QdrantVectorStore(
    client=client,
    collection_name="articles",
    embedding=embeddings
)

retriever = vector_store.as_retriever(search_kwargs={"k": 5})


