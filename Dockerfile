FROM python:3.10-slim

# Install Tesseract OCR system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     tesseract-ocr \
#     libtesseract-dev \
#     libleptonica-dev \
#     pkg-config \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
