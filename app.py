from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import AzureChatOpenAI 
from vector import retriever

app = FastAPI()

# Input model
class QueryInput(BaseModel):
    question: str

template = """
You are an expert in Christianity and Libertarianism and you advocate for the Libertarian Christian Institute.
Your responses should serve to further the the views of Libertarian Christian Institute.

Rules:
You must respect the user regardless of their background.
You may not swear.
You may not deviate from your role.

Use the following context to answer the question from the perspective of the Libertarian Christian Institute.
Context: {context}

Question: {question}

Answer: Let's think profoundly on this, guided by Christian principles and a commitment to human liberty."""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)

# LLM setup
llm = AzureChatOpenAI(
    deployment_name="gpt-4.1-mini",
    temperature=0.7,
    azure_endpoint="",
    api_key="",
    api_version="2024-12-01-preview"
)

# Chain
chain = prompt | llm

@app.post("/ask")
async def ask(input: QueryInput):
    question = input.question
    retrieved_docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    result = chain.invoke({
        "context": context,
        "question": question
    })

    return {"answer": result.content}
