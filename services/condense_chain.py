from langchain.prompts import ChatPromptTemplate
from config.llm import llm

# -------- Condensing Prompt Templates --------
condensed_prompt = ChatPromptTemplate.from_template(
    """
Rephrase the follow-up so it stands alone without prior chat.

Chat history:
{history}

Follow-up question:
{question}

Standalone question:
""".strip()

)
condense_chain = condensed_prompt | llm