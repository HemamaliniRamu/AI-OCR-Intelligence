FROM python:3.13-slim

WORKDIR /app

# Install Tesseract OCR
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Render provides the PORT environment variable
EXPOSE 10000

CMD streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-10000}