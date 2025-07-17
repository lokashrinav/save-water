# 🚀 AquaSpot Render Deployment - Quick Setup

## ✅ Pre-Deployment Checklist

Your repository is now ready for Render deployment with these files:

- ✅ `requirements.txt` - All Python dependencies including Flask and gunicorn
- ✅ `runtime.txt` - Python 3.11.9 specified
- ✅ `Procfile` - Gunicorn configuration for production
- ✅ `wsgi.py` - WSGI entry point
- ✅ `render.yaml` - Optional render-specific configuration
- ✅ Health check endpoint added to `app.py` at `/health`

## 🌐 Deploy to Render

### Option 1: Using Render Dashboard (Recommended)

1. **Go to Render**: Visit [render.com](https://render.com) and sign in
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect Repository**: Select `lokashrinav/save-water`
4. **Configure**:
   - Name: `aquaspot-web`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### Option 2: Using render.yaml (Infrastructure as Code)

1. Push your code to GitHub
2. In Render dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically use the `render.yaml` configuration

## 🔑 Environment Variables

Add these in Render's dashboard under "Environment":

**Required:**
```
COPERNICUS_USERNAME=your_copernicus_username
COPERNICUS_PASSWORD=your_copernicus_password
FLASK_ENV=production
```

**Optional (for email alerts):**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**Optional (for SMS alerts):**
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

## 🎯 Post-Deployment

1. **Test**: Your app will be available at `https://your-service-name.onrender.com`
2. **Health Check**: Visit `https://your-service-name.onrender.com/health`
3. **Upload Test**: Try uploading a pipeline GeoJSON file

## 💡 Production Tips

- **Free Tier**: Service sleeps after 15 min of inactivity (30s cold start)
- **Paid Plans**: For always-on service and better performance
- **Logs**: Monitor build and runtime logs in Render dashboard
- **Custom Domain**: Add your own domain in service settings

## 🐛 Common Issues

- **Build fails**: Check that all packages in requirements.txt are available for Python 3.11
- **GDAL errors**: Render has GDAL pre-installed, but ensure your code handles missing system deps gracefully
- **Memory issues**: Free tier has 512MB RAM limit - consider upgrading for large datasets

Your AquaSpot application is ready to deploy! 🌊
