import json
import requests
from dotenv import load_dotenv
import os
load_dotenv()

# ------------------ Content Moderation ------------------
def is_allowed_content(user_input):
    #print(f"[DEBUG] Checking content moderation for: {user_input!r}")

    analysis = content_analysis(user_input)
    #print(f"[DEBUG] Content analysis result: {json.dumps(analysis, indent=2)}")

    for cat in analysis.get("categoriesAnalysis", []):
        print(f"[DEBUG] Category: {cat['category']}, Severity: {cat['severity']}")
        if cat["category"] == "Hate" and cat["severity"] >= 2:  
            #print("[DEBUG] Blocked due to Hate category.")
            return False
        if cat["category"] == "SelfHarm" and cat["severity"] >= 2:
            #print("[DEBUG] Blocked due to SelfHarm severity.")
            return False
        if cat["category"] == "Sexual" and cat["severity"] >= 3:
            #print("[DEBUG] Blocked due to Sexual severity.")
            return False
        if cat["category"] == "Violence" and cat["severity"] >= 3:
            #print("[DEBUG] Blocked due to Violence severity.")
            return False
    
    #print("[DEBUG] Content passed moderation.")
    return True


def content_analysis(user_input):
    endpoint = os.getenv("AZURE_CONTENT_MOD_ENDPOINT")
    api_key = os.getenv("AZURE_CONTENT_MOD_API")

    url = f"{endpoint}/contentsafety/text:analyze?api-version=2024-09-01"
    headers ={
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': api_key
    }

    payload = {
        "text": user_input,
        "categories": ["Hate", "SelfHarm", "Sexual", "Violence"]
    }

    #print(f"[DEBUG] Sending POST to {url} with headers {headers} and payload {payload}")

    response = requests.post(url, headers=headers, json=payload)
    #print(f"[DEBUG] API Response Status: {response.status_code}")
    
    try:
        data = response.json()
    except Exception as e:
        #print(f"[ERROR] Failed to parse JSON: {e}")
        data = {}
    return data
