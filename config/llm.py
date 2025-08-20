import os
from langchain_openai import AzureChatOpenAI



# -------- LLM Setup --------
llm = AzureChatOpenAI(
    deployment_name="gpt-4.1-mini",
    temperature=0.3,
    top_p=1.0,
    max_tokens=350,
    frequency_penalty=0.2,
    presence_penalty=0.0,
    azure_endpoint=os.getenv("OPENAI_CHAT_ENDPOINT"),
    api_key=os.getenv("OPENAI_CHAT_API"),
    api_version="2024-12-01-preview",
    seed=42
)