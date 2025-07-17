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

# Copy all source code first
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Create data directories in tmp (ephemeral storage)
RUN mkdir -p /tmp/data /tmp/plots /tmp/uploads /tmp/results

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_DIR=/tmp/data
ENV PLOTS_DIR=/tmp/plots
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port for web service (Render will override this)
EXPOSE 5000

# Use gunicorn for production with longer timeout for satellite data processing
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "600", "--worker-class", "sync", "--max-requests", "100"]
