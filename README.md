# AquaSpot

Pipeline leak detection using Sentinel-2 NDWI analysis.

## Overview

AquaSpot is a comprehensive system for detecting potential pipeline leaks through satellite imagery analysis and change detection algorithms. It uses Sentinel-2 satellite data to calculate the Normalized Difference Water Index (NDWI) and detect changes that may indicate pipeline leaks.

## Features

- Sentinel-2 satellite imagery ingestion
- NDWI calculation and change detection
- Geospatial masking for pipeline areas
- Anomaly detection and clustering
- PDF report generation
- Email and SMS alerts
- Command-line interface

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root with your configuration:

```env
# Data directories
DATA_DIR=./data
PLOTS_DIR=./plots

# Sentinel Hub credentials
SENTINEL_USER=your_username
SENTINEL_PASS=your_password

# Email configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Twilio configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE=+1234567890

# Processing parameters
NDWI_THRESHOLD=0.2
MIN_LEAK_AREA_M2=25
PIPELINE_BUFFER_M=100
```

## Usage

### Command Line Interface

Ingest Sentinel-2 imagery:
```bash
aquaspot ingest --geojson pipeline.geojson --date 2025-07-10
```

Run leak detection:
```bash
aquaspot detect --baseline baseline.tif --current current.tif --pipeline pipeline.geojson
```

### Python API

```python
from aquaspot.ingestion import download_sentinel_tiles
from aquaspot.ndwi import calc_ndwi, detect_change
from aquaspot.detection import cluster_anomalies, rank_candidates

# Download imagery
tiles = download_sentinel_tiles(aoi, date, output_dir)

# Calculate NDWI
baseline_ndwi = calc_ndwi(baseline_path)
current_ndwi = calc_ndwi(current_path)

# Detect changes
changes = detect_change(baseline_ndwi, current_ndwi)

# Find leak candidates
candidates = cluster_anomalies(masked_changes, pixel_size)
top_candidates = rank_candidates(candidates)
```

## Development

Run tests:
```bash
pytest
```

Code formatting:
```bash
black aquaspot tests
ruff check aquaspot tests
```

## Project Structure

```
aquaspot/
├── __init__.py
├── config.py          # Configuration management
├── ingestion.py       # Sentinel-2 data fetching
├── ndwi.py            # NDWI calculation and change detection
├── masking.py         # Geospatial masking operations
├── detection.py       # Anomaly clustering and scoring
├── reports.py         # PDF report generation
├── alerts.py          # Email and SMS notifications
└── cli.py             # Command-line interface
```

## License

MIT License
