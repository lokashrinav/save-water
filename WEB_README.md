# AquaSpot Web Interface

A simple and user-friendly web interface for the AquaSpot pipeline leak detection system.

## Features

🌐 **Easy to Use**: Simple drag-and-drop interface for uploading pipeline GeoJSON files  
🛰️ **Automated Analysis**: Automatically downloads satellite data and runs complete analysis  
📊 **Visual Results**: Interactive results page with analysis summary  
📄 **Comprehensive Reports**: Download complete results including PDF reports  
⚡ **Real-time Processing**: Live status updates during analysis  

## Quick Start

### 1. Install Dependencies

```bash
# Install web interface dependencies
pip install -r requirements-web.txt

# Or install everything including development dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

Make sure you have your `.env` file configured with satellite data access credentials:

```bash
cp .env.example .env
# Edit .env with your Copernicus credentials
```

### 3. Start the Web Server

```bash
# Easy startup script
python start_web.py

# Or run directly
python app.py
```

### 4. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## How to Use

1. **Upload Pipeline Data**: Drag and drop your pipeline GeoJSON file
2. **Select Date**: Choose the target date for leak detection analysis
3. **Set Parameters**: Configure the date tolerance (3-10 days)
4. **Start Analysis**: Click "Start Leak Detection Analysis"
5. **Download Results**: Get complete results package with maps and reports

## Supported File Formats

- **GeoJSON** (.geojson): Standard geospatial data format
- **JSON** (.json): JSON files with geospatial data
- **Maximum file size**: 16MB

## Analysis Process

The web interface runs the complete AquaSpot pipeline:

1. **Satellite Data Download**: Retrieves Sentinel-2 imagery for your area and date
2. **NDWI Calculation**: Computes water content indices
3. **Pipeline Masking**: Focuses analysis on pipeline corridors
4. **Change Detection**: Identifies potential leak areas
5. **Report Generation**: Creates comprehensive PDF reports

## Results Package

Your download will include:

- 📊 **Processed satellite imagery**
- 🗺️ **NDWI maps and visualizations**
- 🔍 **Change detection maps**
- 📄 **Professional PDF report**
- 📁 **Raw data files for further analysis**

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB+ RAM recommended for large areas
- **Storage**: 1GB+ free space for processing
- **Internet**: Required for satellite data download

## Troubleshooting

### Analysis Takes Too Long
- Large pipeline areas may take 10-30 minutes
- Consider reducing the area size or date tolerance
- Check your internet connection for satellite data download

### No Satellite Data Found
- Try increasing the days tolerance (7-10 days)
- Check if the date is too recent (Sentinel-2 has ~2-5 day delay)
- Verify your pipeline coordinates are correct

### Upload Fails
- Ensure file is valid GeoJSON format
- Check file size is under 16MB
- Verify file contains valid coordinate data

## Security Notes

- Files are processed locally on your server
- Uploaded files are automatically cleaned up after processing
- No data is sent to external services except for satellite data download

## Production Deployment

For production use:

1. Set `FLASK_ENV=production`
2. Use a proper WSGI server (gunicorn, uWSGI)
3. Configure reverse proxy (nginx, Apache)
4. Set up proper logging and monitoring
5. Configure file upload limits and security

## API Endpoints

- `GET /`: Main upload interface
- `POST /upload`: File upload and analysis trigger
- `GET /download/<timestamp>`: Download results
- `GET /api/status`: Service status check

---

**Need Help?** Check the main [AquaSpot documentation](README.md) or create an issue on GitHub.
