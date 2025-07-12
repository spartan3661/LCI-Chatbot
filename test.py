import requests

# Replace with your actual endpoint
url = "https://rag-chatbot.salmonbeach-1665fbca.eastus.azurecontainerapps.io/ask"

# Your request data
payload = {
    "question": "What is life?"
}

# Make the POST request
response = requests.post(url, json=payload)

# Check if it succeeded
if response.status_code == 200:
    print("Success!")
    print("Response:", response.json())
else:
    print("Error:", response.status_code)
    print("Message:", response.text)
