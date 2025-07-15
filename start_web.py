#!/usr/bin/env python3
"""
Startup script for AquaSpot web interface.

This script sets up the environment and starts the Flask web server
for the AquaSpot pipeline leak detection system.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        print("✓ Flask is installed")
    except ImportError:
        print("✗ Flask not found. Installing web dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-web.txt"])
        print("✓ Web dependencies installed")

def setup_directories():
    """Create required directories."""
    dirs = ['uploads', 'results', 'static', 'templates']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✓ Directories created")

def main():
    """Main startup function."""
    print("🌊 Starting AquaSpot Web Interface...")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Setup directories
    setup_directories()
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  No .env file found. Please create one based on .env.example")
        print("   This is required for satellite data access.")
    
    print("\n🚀 Starting web server...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 AquaSpot web interface stopped.")
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")
        print("💡 Make sure you have all dependencies installed and .env configured.")

if __name__ == "__main__":
    main()
