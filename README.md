# LCI-Chatbot

##Overview
This is the REST endpoint for the LCI website to make chatbot prompt request. This is expected to be dockerized and ran in Azure Container Apps.


##Running Locally
1. Clone this repo
2. Log into Azure and add new NGS rule in Azure VM qdrantdb-lci
3. Run this in the project root:
   ```
   docker build -t lci-rag-chatbot:latest .
   docker run --rm -p 8080:8080 --env-file .env lci-rag-chatbot:latest
   ```

##Updating the Container
To update the image with new features, push to ACR
