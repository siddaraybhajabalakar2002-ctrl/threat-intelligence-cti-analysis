# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Set Python Path so modules resolve correctly
ENV PYTHONPATH="/app/src"

# Expose port
EXPOSE 5000

# Run the application using Gunicorn (Production WSGI Server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--timeout", "0", "api.app:app"]