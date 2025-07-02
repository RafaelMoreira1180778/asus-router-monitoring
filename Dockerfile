FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the exporter script
COPY asus_exporter.py .

# Create non-root user
RUN useradd -m -u 1000 exporter \
    && chown -R exporter:exporter /app
USER exporter

# Expose the metrics port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the exporter
CMD ["python", "asus_exporter.py"]
