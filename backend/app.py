#!/usr/bin/env python3
"""
A15 Framework Patcher - Web API Backend
Flask-based REST API for handling file uploads and framework patching
"""

import os
import json
import uuid
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS

# Import existing patch modules
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    import framework_patch
    import services_patch
    
    # Load miui-service_Patch.py dynamically
    miui_patch_path = os.path.join(parent_dir, "miui-service_Patch.py")
    if os.path.exists(miui_patch_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("miui_service_patch", miui_patch_path)
        if spec and spec.loader:
            miui_service_patch = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(miui_service_patch)
        else:
            miui_service_patch = None
    else:
        miui_service_patch = None
        
except ImportError as e:
    logging.error(f"Failed to import patch modules: {e}")
    framework_patch = None
    services_patch = None
    miui_service_patch = None

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# File to store upload history
HISTORY_FILE = 'upload_history.json'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jar', '.zip'}

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def load_history():
    """Load upload history from file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading history: {e}")
    return []


def save_history(history):
    """Save upload history to file"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving history: {e}")


def process_framework_file(file_path, patch_type):
    """Process uploaded framework file with appropriate patcher"""
    try:
        if patch_type == 'framework' and framework_patch:
            logger.info(f"Processing framework file: {file_path}")
            framework_patch.patch(file_path)
            return True
        elif patch_type == 'services' and services_patch:
            logger.info(f"Processing services file: {file_path}")
            services_patch.patch(file_path)
            return True
        elif patch_type == 'miui-services' and miui_service_patch:
            logger.info(f"Processing MIUI services file: {file_path}")
            miui_service_patch.patch(file_path)
            return True
        else:
            logger.error(f"Unknown patch type or module not available: {patch_type}")
            return False
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'available_patchers': {
            'framework': framework_patch is not None,
            'services': services_patch is not None,
            'miui-services': miui_service_patch is not None
        }
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only .jar and .zip files are supported'}), 400
        
        # Get form data
        device_name = request.form.get('deviceName', '').strip()
        device_version = request.form.get('deviceVersion', '').strip()
        patch_type = request.form.get('patchType', 'framework').strip()
        
        if not device_name or not device_version:
            return jsonify({'error': 'Device name and version are required'}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        filename = f"{file_id}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        logger.info(f"File uploaded: {filename} ({file_size} bytes)")
        
        # Process the file
        processing_success = process_framework_file(file_path, patch_type)
        
        # Create file record
        file_record = {
            'id': file_id,
            'filename': original_filename,
            'uploadedFilename': filename,
            'deviceName': device_name,
            'deviceVersion': device_version,
            'patchType': patch_type,
            'uploadTime': datetime.now().isoformat(),
            'fileSize': file_size,
            'processed': processing_success,
            'downloadUrl': f'/api/download/{file_id}' if processing_success else None
        }
        
        # Add to history
        history = load_history()
        history.insert(0, file_record)  # Add to beginning
        save_history(history)
        
        if processing_success:
            return jsonify({
                'success': True,
                'message': 'File uploaded and processed successfully',
                'file': file_record,
                'downloadUrl': file_record['downloadUrl']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'File uploaded but processing failed',
                'file': file_record
            }), 500
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get upload history"""
    try:
        history = load_history()
        return jsonify({
            'success': True,
            'files': history
        })
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': 'Failed to load history'}), 500


@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download processed file"""
    try:
        history = load_history()
        file_record = next((f for f in history if f['id'] == file_id), None)
        
        if not file_record:
            abort(404)
        
        # Look for processed file first, then original
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], file_record['uploadedFilename'])
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record['uploadedFilename'])
        
        if os.path.exists(processed_path):
            return send_file(processed_path, as_attachment=True, download_name=f"patched_{file_record['filename']}")
        elif os.path.exists(original_path):
            return send_file(original_path, as_attachment=True, download_name=file_record['filename'])
        else:
            abort(404)
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        abort(500)


@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete file and remove from history"""
    try:
        history = load_history()
        file_record = next((f for f in history if f['id'] == file_id), None)
        
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Remove files
        for folder in [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]:
            file_path = os.path.join(folder, file_record['uploadedFilename'])
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        
        # Remove from history
        history = [f for f in history if f['id'] != file_id]
        save_history(history)
        
        return jsonify({'success': True, 'message': 'File deleted successfully'})
        
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return jsonify({'error': 'Failed to delete file'}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting A15 Patcher Web API on port {port}")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Processed folder: {app.config['PROCESSED_FOLDER']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)