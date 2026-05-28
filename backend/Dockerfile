# Render Docker web service — set Root Directory to `backend` in Render dashboard
FROM python:3.11-slim

# System deps for Tesseract OCR (ticket image upload)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render injects PORT at runtime (often 10000); default for local docker run
ENV PORT=10000
EXPOSE 10000

# FastAPI app lives at backend/app/main.py → app.main:app
# Local run (from backend/): docker build -t seatswap-api . && docker run --env-file .env -p 8000:10000 seatswap-api
# Render: set MONGODB_URL, SECRET_KEY, etc. in the service Environment tab (no .env file in the image)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
