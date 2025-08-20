from fastapi import APIRouter
from schemas.query_input import QueryInput
from services.chat_chain import chat_chain
from services.condense_chain import condense_chain
from utils.helpers import to_chat_messages, build_hist_text_for_condense
from services.vector import retriever
from utils.azure_blob_utils import log_question
from services.sentiment_analysis import get_sentiment
from services.content_moderation import is_allowed_content
import os

router = APIRouter()

@router.post("/ask")
async def ask(input: QueryInput):

    # Content Moderation
    harmful_content = is_allowed_content(input.question)
    if not harmful_content:
        return {"answer": "Content blocked due to policy.",
                "promptFlag": False,
                "delayPrompt": True}


    chat_history = to_chat_messages(input.history)
    #print("DEBUG CHAT HISTORY", chat_history)
    # Sentiment Analysis
    showPrompt = False
    if not input.alreadyPrompted:
        showPrompt = get_sentiment(chat_history[-4:], input.question)
    if os.getenv("STORE_QUESTION") == "1":
        log_question("chat-logs", "logs", input.question, input.time)

    # Use last 6 messages for condensation
    hist_for_condense = chat_history[-6:]
    hist_text = build_hist_text_for_condense(hist_for_condense)

    # Condense only if history exists
    standalone_question = input.question
    if hist_for_condense:
        condensed = await condense_chain.ainvoke({
            "history": hist_text,
            "question": input.question
        })
        standalone_question = condensed.content.strip()

    # Context
    docs = await retriever.ainvoke(standalone_question)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    result = await chat_chain.ainvoke({
        "history": chat_history,
        "context": context,
        "question": input.question,
    })

    return {"answer": result.content,
            "promptFlag": showPrompt,
            "delayPrompt": False}   
    