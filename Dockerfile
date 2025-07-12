FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY app.py vector.py requirements.txt /app/
COPY chroma_langchain_db/ /app/chroma_langchain_db/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
