# Use Python 3.10 slim image (broad prebuilt wheel support)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install essential build dependencies for binary extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel to fetch precompiled manylinux wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm || true

# Copy application code
COPY . .

# Set Python Path so modules resolve correctly
ENV PYTHONPATH="/app/src"

# Expose port
EXPOSE 5000

# Run the application using Gunicorn (Production WSGI Server)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 8 --timeout 120 api.app:app"]