"""
WSGI entry point for AquaSpot web application.

This file is used by production servers like Gunicorn to run the Flask app.
"""

from app import app

if __name__ == "__main__":
    app.run()