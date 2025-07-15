FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY aquaspot/ ./aquaspot/
COPY README.md .

# Create data directories
RUN mkdir -p data plots

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_DIR=/app/data
ENV PLOTS_DIR=/app/plots

# Expose port for Streamlit (if running web interface)
EXPOSE 8501

# Default command
CMD ["python", "-m", "aquaspot.cli", "--help"]
