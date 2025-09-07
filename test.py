"""
async def ask(input: QueryInput):

    # Content Moderation
    hasHarm = False
    harmful_content = is_allowed_content(input.question)
    if not harmful_content:
        return {"answer": "Content blocked due to policy.",
                "promptFlag": False,
                "delayPrompt": True}
    else:
        hasHarm = True

    chat_history = to_chat_messages(input.history)
    #print("DEBUG CHAT HISTORY", chat_history)
    # Sentiment Analysis
    showPrompt = False
    if not input.alreadyPrompted:
        showPrompt = get_sentiment(chat_history[-4:], input.question)
    if os.getenv("STORE_QUESTION") == "1":
        log_question("chat-logs", "logs", input.question, input.time, showPrompt, hasHarm)

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
    docs = docs or []


    return
    for i, d in enumerate(docs[:3], start=1):
        md = getattr(d, "metadata", {}) or {}
        pid = d.metadata.get("_id")
        data = get_payload()
        print(f"DEBUG doc #{i} metadata keys: {list(md.keys())} -> {md}")  # adjust to logger.info in prod

    return
    cited_chunks = []
    seen_urls = set()
    links = []                
    max_sources = int(os.getenv("MAX_SOURCES", 5))

    for i, d in enumerate(docs[:max_sources], start=1):
        token = f"[S{i}]"
        chunk_text = getattr(d, "page_content", None) or ""
        cited_chunks.append(f"{token} {chunk_text}")

        md = getattr(d, "metadata", {}) or {}
        url = md.get("link") or None
        title = md.get("title") or None

        if url and url not in seen_urls:
            seen_urls.add(url)
            links.append((token, url, title))
    if cited_chunks:
        context = "\n\n".join(cited_chunks)
    else:
        # fallback context (no tokens available)
        context = "\n\n".join(getattr(d, "page_content", "") for d in docs)

    #print(context[:1000])

    result = await chat_chain.ainvoke({
        "history": chat_history,
        "context": context,
        "question": input.question,
    })

    answer_text = result.content

    if links:
        print("Links Found!")
        answer_text += "\n\nSources:\n"
        for token, url, title in links:
            if title:
                answer_text += f"{token} [{title}]({url})\n"
            else:
                answer_text += f"{token} {url}\n"
    else:
        answer_text += "\n\nSources: No retrieved articles found for this query."

    return {"answer": answer_text,
            "promptFlag": showPrompt,
            "delayPrompt": False}   
    


"""