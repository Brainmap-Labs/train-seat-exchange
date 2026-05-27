# Use an official lightweight Python image
FROM python:3.11-slim

# Install system dependencies, including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
溜 pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port Render expects (Render sets the PORT env variable automatically)
EXPOSE 10000

# Start your application (replace 'main:app' with your actual Uvicorn/Gunicorn entry point)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]