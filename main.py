from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import AzureChatOpenAI 
from vector import retriever
from dotenv import load_dotenv
import os

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question:
{question}
"""
)

llm = AzureChatOpenAI(
    deployment_name="gpt-4.1-mini",
    temperature=0.7,
    azure_endpoint=os.getenv("OPENAI_CHAT_ENDPOINT"),
    api_key=os.getenv("OPENAI_API"),
    api_version="2024-12-01-preview"
)

question = "What are the core beliefs of Libertarian Christianity?"

chain = prompt | llm

retrieved_docs = retriever.invoke(question)
context = "\n\n".join([doc.page_content for doc in retrieved_docs])

response = chain.invoke({

    "context": context,
    "question": question
})
print(response.content)
