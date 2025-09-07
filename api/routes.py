from fastapi import APIRouter
from schemas.query_input import QueryInput
from services.chat_chain import chat_chain
from services.condense_chain import condense_chain
from utils.helpers import to_chat_messages, build_hist_text_for_condense
from services.vector import retrieve_documents_with_payload 
from utils.azure_blob_utils import log_question
from services.sentiment_analysis import get_sentiment
from services.content_moderation import is_allowed_content
from starlette.concurrency import run_in_threadpool
import os


def _qdrant_search_sync(client, collection_name, query_vector, limit):
    return client.search(collection_name=collection_name, query_vector=query_vector, limit=limit, with_payload=True)

async def qdrant_search_with_payload_async(qdrant_client, collection_name, query_text, embeddings, limit=5):
    limit = int(limit or 5)

    qvec = embeddings.embed_documents([query_text])[0]

    hits = await run_in_threadpool(_qdrant_search_sync, qdrant_client, collection_name, qvec, limit)

    results = []
    for h in hits:
        payload = None
        score = None
        pid = None

        if hasattr(h, "payload"):
            payload = getattr(h, "payload")
        elif isinstance(h, dict):
            payload = h.get("payload")

        if hasattr(h, "id"):
            pid = getattr(h, "id")
        elif isinstance(h, dict):
            pid = h.get("id") or h.get("point_id") or h.get("payload", {}).get("_id")

        payload = payload or {}
        if not isinstance(payload, dict):
            try:
                payload = dict(payload)
            except Exception:
                payload = {}

        text = payload.get("page_content") or payload.get("text") or ""
        results.append({"payload": payload, "text": text, "score": score, "id": pid})

    return results

router = APIRouter()

@router.post("/ask")
async def ask(input: QueryInput):
    chat_history = to_chat_messages(input.history)

    hist_for_condense = chat_history[-6:]
    hist_text = build_hist_text_for_condense(hist_for_condense)
    standalone_question = input.question
    if hist_for_condense:
        condensed = await condense_chain.ainvoke({"history": hist_text, "question": input.question})
        standalone_question = condensed.content.strip()

    docs = await retrieve_documents_with_payload(standalone_question)
    docs = docs or []

    cited_chunks = []
    links = []
    seen_urls = set()
    for i, d in enumerate(docs, start=1):
        token = f"[S{i}]"
        page = d.page_content or ""
        cited_chunks.append(f"{token} {page}")
        md = d.metadata or {}
        url = md.get("link") or md.get("url") or md.get("source")
        title = md.get("title") or md.get("page_title") or None

        if url and url not in seen_urls:
            seen_urls.add(url)
            links.append((token, url, title))

    """
    for link in links:
    print(link)
    """


    # assemble context
    context = "\n\n".join(cited_chunks) if cited_chunks else ""
    #print(context[:1000])

    result = await chat_chain.ainvoke({
        "history": chat_history,
        "context": context,
        "question": input.question,
    })

    answer_text = result.content

    # map links in source
    if links:
        answer_text += "\n\nSources:\n"
        for token, url, title in links:
            if title:
                answer_text += f"{token} [{title}]({url})\n"
            else:
                answer_text += f"{token} {url}\n"
    else:
        answer_text += "\n\nSources: No retrieved articles found for this query."

    return {"answer": answer_text, "promptFlag": False, "delayPrompt": False}