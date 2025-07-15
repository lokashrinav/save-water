"""
Simple web frontend for AquaSpot pipeline leak detection.

This Flask application provides a user-friendly interface for running
AquaSpot leak detection analysis through a web browser.
"""

import os
import json
import zipfile
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import shutil

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import logging

# Import AquaSpot CLI
from aquaspot.cli import main as aquaspot_cli

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

RESULTS_FOLDER = Path('results')
RESULTS_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'geojson', 'json'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start analysis."""
    if 'geojson_file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['geojson_file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename
        file.save(file_path)
        
        # Get form data
        target_date = request.form.get('target_date')
        days_tolerance = int(request.form.get('days_tolerance', 5))
        
        try:
            # Validate date
            date_obj = datetime.strptime(target_date, '%Y-%m-%d')
            
            # Start analysis
            return run_analysis(file_path, date_obj, days_tolerance)
            
        except ValueError as e:
            flash(f'Invalid date format: {e}')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            flash(f'Analysis failed: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a GeoJSON file.')
    return redirect(url_for('index'))

def run_analysis(geojson_path, target_date, days_tolerance):
    """Run the AquaSpot analysis pipeline using CLI."""
    try:
        # Create unique output directory for this analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = RESULTS_FOLDER / f'analysis_{timestamp}'
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Starting analysis for {geojson_path} on {target_date}")
        
        # Step 1: Use CLI to ingest data
        ingest_cmd = [
            'python', '-m', 'aquaspot.cli', 'ingest',
            '--geojson', str(geojson_path),
            '--date', target_date.strftime('%Y-%m-%d'),
            '--output', str(output_dir),
            '--days-tolerance', str(days_tolerance)
        ]
        
        logger.info("Running data ingestion...")
        result = subprocess.run(ingest_cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode != 0:
            raise Exception(f"Data ingestion failed: {result.stderr}")
        
        # Find downloaded images
        image_files = list(output_dir.glob('**/*.tif'))
        if len(image_files) < 2:
            logger.warning("Only found 1 image - change detection may be limited")
        
        # Step 2: Try to run detection if we have multiple images
        change_files = []
        if len(image_files) >= 2:
            try:
                # Sort by date and use first two for comparison
                image_files.sort()
                baseline_img = image_files[0]
                current_img = image_files[1]
                
                detect_cmd = [
                    'python', '-m', 'aquaspot.cli', 'detect',
                    str(baseline_img),
                    str(current_img),
                    str(geojson_path),
                    '--output', str(output_dir / 'detection_results')
                ]
                
                logger.info("Running change detection...")
                result = subprocess.run(detect_cmd, capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    change_files = list((output_dir / 'detection_results').glob('**/*.tif'))
                else:
                    logger.warning(f"Change detection had issues: {result.stderr}")
            
            except Exception as e:
                logger.warning(f"Change detection failed: {e}")
        
        # Create simple analysis summary
        summary_path = output_dir / 'analysis_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(f"AquaSpot Analysis Summary\n")
            f.write(f"========================\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target Date: {target_date.strftime('%Y-%m-%d')}\n")
            f.write(f"Pipeline File: {geojson_path.name}\n")
            f.write(f"Days Tolerance: {days_tolerance}\n\n")
            f.write(f"Results:\n")
            f.write(f"- Images Found: {len(image_files)}\n")
            f.write(f"- Change Maps: {len(change_files)}\n\n")
            f.write(f"Files Generated:\n")
            for img in image_files:
                f.write(f"  - {img.relative_to(output_dir)}\n")
            for change in change_files:
                f.write(f"  - {change.relative_to(output_dir)}\n")
        
        # Create results package
        results_zip = create_results_package(output_dir, timestamp)
        
        logger.info("Analysis completed successfully")
        
        return render_template('results.html', 
                             timestamp=timestamp,
                             report_available=True,
                             num_images=len(image_files),
                             num_changes=len(change_files))
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

def create_results_package(output_dir, timestamp):
    """Create a ZIP file with all results."""
    zip_path = RESULTS_FOLDER / f'aquaspot_results_{timestamp}.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(output_dir)
                zipf.write(file_path, arc_name)
    
    return zip_path

@app.route('/download/<timestamp>')
def download_results(timestamp):
    """Download results ZIP file."""
    zip_path = RESULTS_FOLDER / f'aquaspot_results_{timestamp}.zip'
    if zip_path.exists():
        return send_file(zip_path, as_attachment=True)
    else:
        flash('Results not found')
        return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """API endpoint to check service status."""
    return jsonify({
        'status': 'running',
        'service': 'AquaSpot Pipeline Leak Detection',
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 16MB.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure required directories exist
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    RESULTS_FOLDER.mkdir(exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
