# 🌊 AquaSpot Render Deployment Guide

This guide will help you deploy your AquaSpot application to Render, a modern cloud platform that makes deployment simple.

## 🚀 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Environment Variables**: Have your Copernicus/Sentinel Hub credentials ready

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your Repository

Your repository should have these files (✅ already present):
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `Procfile` - How to start your app
- `wsgi.py` - WSGI entry point
- `app.py` - Your Flask application

### Step 2: Connect to Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select your repository: `lokashrinav/save-water`

### Step 3: Configure Your Web Service

Fill in these settings:

**Basic Settings:**
- **Name**: `aquaspot-web` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (deploys automatically on git push)

### Step 4: Set Environment Variables

Add these environment variables in Render:

**Required:**
```
COPERNICUS_USERNAME=your_username
COPERNICUS_PASSWORD=your_password
FLASK_ENV=production
```

**Optional (for features):**
```
# For email alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# For SMS alerts (if using Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Watch the build logs for any issues

### Step 6: Access Your Application

Once deployed, you'll get a URL like:
`https://aquaspot-web.onrender.com`

## 🔧 Configuration Tips

### Build Performance
Render's free tier has build time limits. If builds are slow:
- Consider upgrading to a paid plan for faster builds
- Optimize your `requirements.txt` (only include needed packages)

### File Storage
Render's file system is ephemeral. For persistent storage:
- Use external services for large files
- Results are packaged as downloads for users

### Security
- Never commit secrets to your repository
- Use Render's environment variables for all credentials
- Enable HTTPS (automatic on Render)

## 🐛 Troubleshooting

### Common Issues:

**Build Fails:**
- Check that all dependencies in `requirements.txt` are available
- Ensure Python version matches `runtime.txt`
- Review build logs for specific error messages

**App Won't Start:**
- Verify your `wsgi.py` imports correctly
- Check that Flask app is named `app` in `app.py`
- Ensure port binding is correct: `0.0.0.0:$PORT`

**Geospatial Libraries Issues:**
- GDAL dependencies are pre-installed on Render
- If you get GDAL errors, try adding system dependencies

**Memory Issues:**
- Free tier has 512MB RAM limit
- Consider upgrading for larger datasets
- Optimize memory usage in your code

### Getting Help:
- Check Render's documentation: [render.com/docs](https://render.com/docs)
- View your service logs in the Render dashboard
- Contact Render support if needed

## 🎯 Next Steps

After successful deployment:

1. **Test Your Application**: Upload a test pipeline GeoJSON
2. **Monitor Performance**: Use Render's metrics dashboard
3. **Set Up Custom Domain** (optional): Add your own domain name
4. **Enable Notifications**: Set up alerts for downtime

## 📈 Scaling

As your usage grows:
- **Upgrade Plan**: More RAM and CPU
- **Add Workers**: Handle more concurrent users
- **Database**: Add PostgreSQL for persistent data
- **CDN**: Speed up static file delivery

---

Your AquaSpot application is now live and accessible to users worldwide! 🌍