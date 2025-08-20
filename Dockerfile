FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

# work directory
WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# non-root
RUN useradd -m appuser
USER appuser

ENV PORT=8080
EXPOSE 8080

# start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
