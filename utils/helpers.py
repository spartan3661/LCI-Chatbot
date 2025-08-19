from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import List, Dict

def to_chat_messages(history_dicts: List[Dict[str, str]]):
    """Convert list of {role, content} dicts into LangChain message objects."""
    msgs = []
    for msg in history_dicts:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "user":
            msgs.append(HumanMessage(content=content))
        if role == "assistant":
            msgs.append(AIMessage(content=content))
    return msgs

def build_hist_text_for_condense(messages: List[BaseMessage]):
    """Turn last N messages into a simple text transcript for the condense step."""
    return "\n".join(f"{m.type}: {m.content}" for m in messages)
