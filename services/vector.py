from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from starlette.concurrency import run_in_threadpool
from langchain_core.documents import Document
import os

embeddings = AzureOpenAIEmbeddings(
    deployment="text-embedding-3-small", 
    model="text-embedding-3-small",
    azure_endpoint=os.getenv("OPENAI_EMBEDDINGS_ENDPOINT"),
    api_key=os.getenv("OPENAI_EMBEDDINGS_API"),
    api_version="2024-02-01"
)

client = QdrantClient(host=os.environ.get("QDRANT_HOST_EXTERNAL"), 
                      port=int(os.environ.get("QDRANT_PORT", 6333)),
                      api_key=os.environ.get("QDRANT_API"),
                      https=False)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="articles",
    embedding=embeddings
)

def _embed_sync(emb, text: str):
    """Return embedding for a single text (list[float])"""
    if hasattr(emb, "embed_query"):
        return emb.embed_query(text)
    return emb.embed_documents([text])[0]


def _qdrant_search_sync(qdrant_client: QdrantClient, collection_name: str, query_vector, limit: int):
    return qdrant_client.search(collection_name=collection_name, query_vector=query_vector, limit=limit, with_payload=True)


# --- public API: retrieve Documents with payload present in metadata ---
async def retrieve_documents_with_payload(query, k = 5, collection_name="articles"):
    """
    Returns a list of langchain_core.documents.Document objects where
    Document.page_content is the stored page_content (if present) and
    Document.metadata contains the payload (link/title/...) plus '_id'.

    This function runs blocking calls in a threadpool to keep FastAPI async-safe.
    """
    try:
        max_k = int(k) if k is not None else int(os.getenv("MAX_SOURCES", "5"))
    except (ValueError, TypeError):
        max_k = 5

    #embedding call may be blocking
    qvec = await run_in_threadpool(_embed_sync, embeddings, query)

    # search qdrant in threadpool
    hits = await run_in_threadpool(_qdrant_search_sync, client, collection_name, qvec, max_k)

    docs = []
    for h in hits:
        payload = None
        pid = None
        score = None

        if hasattr(h, "payload"):
            payload = getattr(h, "payload")
        elif isinstance(h, dict):
            payload = h.get("payload") or {}

        if hasattr(h, "id"):
            pid = getattr(h, "id")
        elif isinstance(h, dict):
            pid = h.get("id") or h.get("point_id") or (payload or {}).get("_id")

        payload = payload or {}
        if not isinstance(payload, dict):
            try:
                payload = dict(payload)
            except Exception:
                payload = {}

        text = payload.get("page_content") or ""

        metadata = dict(payload) 
        if pid:
            metadata["_id"] = pid
        if score is not None:
            metadata["_score"] = score
        metadata["_collection_name"] = collection_name
        docs.append(Document(page_content=text, metadata=metadata))
    return docs

#retriever = vector_store.as_retriever(search_kwargs={"k": os.getenv("MAX_SOURCES"), "with_payload": True})


