# AquaSpot Overview

AquaSpot is a leak detection system that analyzes Sentinel-2 satellite imagery to find abnormal increases in surface water near pipelines.

## Idea Summary

- **Goal**: Provide an accessible tool for utilities and environmental teams to spot potential pipeline leaks before they escalate.
- **Approach**: Compare satellite images over time using the Normalized Difference Water Index (NDWI) and highlight areas of change.

## Project Description

**What it does**

AquaSpot ingests satellite data, calculates NDWI, and reports where sudden water spikes might indicate a leak. Results are available through a command line interface or an easy web interface.

**Who it helps**

Operators monitoring long pipeline networks and environmental agencies can quickly identify suspicious areas and prioritize inspections.

**How it works**

1. Download Sentinel‑2 imagery for the pipeline corridor.
2. Compute NDWI values to map water presence.
3. Detect significant changes between baseline and current imagery.
4. Cluster anomalies and create visual reports.

**Why it matters**

Undetected leaks waste resources and damage local ecosystems. AquaSpot offers a scalable way to monitor pipelines remotely and reduce response times.

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```
   For development:
   ```bash
   pip install -e ".[dev]"
   ```
2. Configure environment variables in `.env` as shown in `README.md`.
3. Run the web interface:
   ```bash
   python start_web.py
   ```
   Visit `http://localhost:5000` to upload your pipeline GeoJSON and start analysis.

## Tech Stack

- **Python 3.11**
- **Rasterio** and **Shapely** for geospatial processing
- **Geopandas**, **numpy**, and **pandas** for data analysis
- **Flask** and **Streamlit** provide web and CLI interfaces
- **WeasyPrint** generates PDF reports

---
See `README.md` for full documentation and advanced usage.