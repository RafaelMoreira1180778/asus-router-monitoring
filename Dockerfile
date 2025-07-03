FROM python:3.12-slim

# Set metadata
LABEL maintainer="Rafael"
LABEL description="ASUS Router Prometheus Exporter v2.0 - Modular Architecture"
LABEL version="2.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ src/
COPY asus_exporter.py .

# Create non-root user for security
RUN useradd -m -u 1000 exporter \
    && chown -R exporter:exporter /app
USER exporter

# Expose the metrics port
EXPOSE 8000

# Health check - updated for new endpoint structure
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8000/health || exit 1

# Set default environment variables
ENV ASUS_HOSTNAME=192.168.1.1
ENV ASUS_USERNAME=admin
ENV ASUS_USE_SSL=false
ENV EXPORTER_PORT=8000
ENV EXPORTER_COLLECTION_INTERVAL=15
ENV EXPORTER_LOG_LEVEL=INFO
ENV EXPORTER_CACHE_TIME=5

# Run the modular exporter
CMD ["python", "asus_exporter.py"]
