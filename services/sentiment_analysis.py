import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv
load_dotenv()


# ------------------ Sentiment Analysis ------------------
def get_sentiment(history, question, threshold=0.7):
    if not history or len(history) < 4:
        #print(f"[DEBUG] Not enough history ({len(history) if history else 0}). Skipping sentiment analysis.")
        return False

    #print(f"[DEBUG] Running sentiment analysis on last 4 messages.")
    endpoint = os.getenv("AZURE_SENTIMENT_ENDPOINT")
    api_key = os.getenv("AZURE_SENTIMENT_API")

    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    document = " ".join(
        str(getattr(item, "content", "")).strip()
        for item in history
        if getattr(item, "content", "").strip()
    )
    document += f" {question.strip()}"
    #print(f"[DEBUG] Combined history text: {document!r}")

    
    if not document:
        #print("[DEBUG] No valid text found in history. Skipping sentiment analysis.")
        return False

    response = client.analyze_sentiment([document])
    result = response[0]


    #print(f"[DEBUG] Sentiment: {result.sentiment}, Scores: {result.confidence_scores}")
    if result.sentiment == "positive" and result.confidence_scores.positive >= threshold:
        #print("[DEBUG] Positive sentiment above threshold.")
        return True
    
    #print("[DEBUG] Sentiment did not meet positive threshold.")
    return False