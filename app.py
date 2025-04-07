import os
import logging
import tempfile
import time
import uuid
from zipfile import ZipFile
from pathlib import Path

from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename

from utils import process_zip_file, cleanup_old_files

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'zip'}

# Create a directory to store processed files
PROCESSED_FILES_DIR = os.path.join(UPLOAD_FOLDER, 'processed_docs')
os.makedirs(PROCESSED_FILES_DIR, exist_ok=True)

# Configure session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Clean up old files to prevent disk space issues
    cleanup_old_files(PROCESSED_FILES_DIR, max_age_hours=24)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .zip files are allowed'}), 400
    
    try:
        # Generate a unique session ID if not already set
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        
        # Create a session-specific directory for this user's files
        user_dir = os.path.join(PROCESSED_FILES_DIR, session_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save the uploaded file
        zip_path = os.path.join(user_dir, secure_filename(file.filename))
        file.save(zip_path)
        
        # Check if it's a valid zip file
        try:
            with ZipFile(zip_path, 'r') as zip_ref:
                # Quick check of zip validity
                file_count = len([f for f in zip_ref.namelist() 
                                if f.lower().endswith(('.doc', '.docx'))])
                if file_count == 0:
                    return jsonify({'error': 'No .doc or .docx files found in the ZIP archive'}), 400
                
                return jsonify({
                    'message': 'File uploaded successfully',
                    'zip_path': zip_path,
                    'file_count': file_count
                }), 200
        except Exception as e:
            logger.error(f"Error validating zip file: {e}")
            return jsonify({'error': 'Invalid or corrupted ZIP file'}), 400
        
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        return jsonify({'error': 'An error occurred during upload'}), 500

@app.route('/process', methods=['POST'])
def process_file():
    data = request.json
    zip_path = data.get('zip_path')
    
    if not zip_path or not os.path.exists(zip_path):
        return jsonify({'error': 'Invalid file path'}), 400
    
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session expired'}), 400
            
        user_dir = os.path.join(PROCESSED_FILES_DIR, session_id)
        
        # Process the ZIP file (extract, merge, convert to PDF)
        result = process_zip_file(zip_path, user_dir)
        
        if result['success']:
            # Return the paths to the processed files
            return jsonify({
                'message': 'Processing completed successfully',
                'docx_path': result['docx_path'],
                'pdf_path': result['pdf_path'],
                'processed_files': result['processed_files'],
                'failed_files': result['failed_files']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Error in processing: {e}")
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500

@app.route('/download/<file_type>')
def download_file(file_type):
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session expired'}), 400
            
        user_dir = os.path.join(PROCESSED_FILES_DIR, session_id)
        
        if file_type == 'docx':
            file_path = os.path.join(user_dir, 'merged_document.docx')
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            download_name = 'merged_document.docx'
        elif file_type == 'pdf':
            file_path = os.path.join(user_dir, 'merged_document.pdf')
            mime_type = 'application/pdf'
            download_name = 'merged_document.pdf'
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 404
            
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"Error in download: {e}")
        return jsonify({'error': f'An error occurred during download: {str(e)}'}), 500

@app.route('/status')
def processing_status():
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session expired'}), 400
            
        user_dir = os.path.join(PROCESSED_FILES_DIR, session_id)
        status_file = os.path.join(user_dir, 'status.json')
        
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                import json
                status = json.load(f)
            return jsonify(status), 200
        else:
            return jsonify({'status': 'unknown'}), 404
            
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({'error': 'Error checking processing status'}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Internal server error"), 500
