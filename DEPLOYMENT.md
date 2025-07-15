# 🌊 AquaSpot Deployment Guide

This guide shows how to deploy the AquaSpot web interface so others can easily use your pipeline leak detection system.

## 🚀 Quick Deployment

### Option 1: Local Development Server

```bash
# 1. Clone the repository
git clone https://github.com/lokashrinav/save-water.git
cd save-water

# 2. Install dependencies
pip install -e .
pip install Flask==2.3.3 Werkzeug==2.3.7

# 3. Configure environment
cp .env.example .env
# Edit .env with your Copernicus credentials

# 4. Start the web server
python start_web.py
```

Visit `http://localhost:5000` in your browser!

### Option 2: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python dependencies
RUN pip install -e .
RUN pip install Flask==2.3.3 Werkzeug==2.3.7

# Create directories
RUN mkdir -p uploads results static templates

# Expose port
EXPOSE 5000

# Start application
CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t aquaspot-web .
docker run -p 5000:5000 -v $(pwd)/.env:/app/.env aquaspot-web
```

### Option 3: Cloud Deployment (Railway/Heroku)

1. **Create `requirements.txt`:**
```txt
Flask==2.3.3
Werkzeug==2.3.7
rasterio
geopandas
planetary-computer
pystac-client
requests
shapely
numpy
click
python-dotenv
```

2. **Create `Procfile`:**
```
web: python app.py
```

3. **Deploy to Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Copernicus Data Space Ecosystem credentials
CDSE_USERNAME=your_username
CDSE_PASSWORD=your_password

# Optional: Custom data directory
DATA_DIR=./my_data

# Optional: Email/SMS alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
```

### File Limits

Default settings in `app.py`:
- Maximum file size: 16MB
- Supported formats: `.geojson`, `.json`
- Processing timeout: No limit (depends on area size)

## 🌐 Making It Public

### Option 1: Ngrok (Quick Testing)

```bash
# Install ngrok
pip install pyngrok

# Start your app
python start_web.py

# In another terminal, expose it
ngrok http 5000
```

Share the ngrok URL with others!

### Option 2: Cloud Platforms

**Railway (Recommended):**
- Easy deployment from GitHub
- Automatic HTTPS
- Custom domains
- $5/month for small usage

**Heroku:**
- Free tier available
- Easy scaling
- Add-ons for databases

**DigitalOcean App Platform:**
- $5/month basic plan
- Automatic HTTPS
- Easy scaling

### Option 3: Self-Hosted VPS

```bash
# On Ubuntu/Debian VPS
sudo apt update
sudo apt install python3 python3-pip nginx

# Clone and setup your app
git clone https://github.com/lokashrinav/save-water.git
cd save-water
pip3 install -e .
pip3 install gunicorn Flask==2.3.3 Werkzeug==2.3.7

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/aquaspot
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📱 User Instructions

Share these instructions with your users:

### How to Use AquaSpot Web Interface

1. **Prepare Your Data:**
   - Create a GeoJSON file with your pipeline geometry
   - Use tools like [geojson.io](https://geojson.io) to create/edit GeoJSON files
   - Ensure coordinates are in WGS84 (EPSG:4326) format

2. **Upload and Analyze:**
   - Visit the AquaSpot web interface
   - Drag & drop your GeoJSON file
   - Select the target date for analysis
   - Choose days tolerance (3-10 days recommended)
   - Click "Start Leak Detection Analysis"

3. **Download Results:**
   - Wait for analysis to complete (5-30 minutes depending on area size)
   - Download the complete results package
   - Review the analysis summary and any detected changes

### Sample GeoJSON

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Pipeline Segment 1",
        "type": "gas_pipeline"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [-95.3698, 29.7604],
          [-95.3595, 29.7504],
          [-95.3492, 29.7404]
        ]
      }
    }
  ]
}
```

## 🔒 Security Considerations

For production deployment:

1. **Environment Variables:**
   - Never commit `.env` files
   - Use platform-specific environment variable systems

2. **File Upload Security:**
   - The app already validates file types
   - Consider adding virus scanning for production

3. **Rate Limiting:**
   - Add rate limiting for uploads
   - Consider user authentication for heavy usage

4. **HTTPS:**
   - Always use HTTPS in production
   - Most cloud platforms provide this automatically

## 📊 Usage Analytics

To track usage, consider adding:

1. **Simple Analytics:**
```python
import sqlite3
from datetime import datetime

# Log analysis requests
def log_analysis(geojson_filename, target_date, user_ip):
    conn = sqlite3.connect('analytics.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analyses 
        (id INTEGER PRIMARY KEY, filename TEXT, date TEXT, 
         ip TEXT, timestamp TEXT)
    ''')
    conn.execute(
        'INSERT INTO analyses (filename, date, ip, timestamp) VALUES (?, ?, ?, ?)',
        (geojson_filename, target_date, user_ip, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
```

2. **Performance Monitoring:**
   - Use tools like Sentry for error tracking
   - Monitor memory usage for large analyses
   - Set up alerts for failed analyses

## 💡 Tips for Success

1. **Start Small:** Test with small pipeline areas first
2. **Clear Instructions:** Provide examples and documentation
3. **Support:** Set up a contact method for user questions
4. **Feedback:** Collect user feedback to improve the interface
5. **Updates:** Keep the system updated with latest satellite data

---

**Need Help?** 
- Check the [main documentation](README.md)
- Create an issue on GitHub
- Contact the development team

🌊 Happy leak detecting!
