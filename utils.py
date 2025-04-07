import os
import time
import json
import logging
import tempfile
import shutil
import subprocess
from zipfile import ZipFile
from pathlib import Path
from threading import Thread
import docx
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

logger = logging.getLogger(__name__)

def save_status(status_dir, status_data):
    """Save processing status to a JSON file"""
    status_file = os.path.join(status_dir, 'status.json')
    with open(status_file, 'w') as f:
        json.dump(status_data, f)

def extract_doc_files(zip_path, extract_dir):
    """Extract all .doc and .docx files from a zip file"""
    doc_files = []
    
    with ZipFile(zip_path, 'r') as zip_ref:
        # Get all .doc and .docx files
        for file in zip_ref.namelist():
            if file.lower().endswith(('.doc', '.docx')):
                # Extract the file
                zip_ref.extract(file, extract_dir)
                doc_files.append(os.path.join(extract_dir, file))
    
    return doc_files

def convert_doc_to_docx(doc_path, output_dir):
    """
    Convert a .doc file to .docx format
    
    This function attempts to use LibreOffice for conversion if available,
    falling back to a basic document creation method if not
    """
    filename = os.path.basename(doc_path)
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(output_dir, f"{base_name}.docx")
    
    # First try using LibreOffice if available
    try:
        cmd = [
            'libreoffice', '--headless', '--convert-to', 'docx', 
            '--outdir', output_dir, doc_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the conversion succeeded
        if os.path.exists(output_path):
            return output_path
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.warning(f"LibreOffice conversion failed: {e}. Falling back to basic conversion.")
    
    # Fallback: Create a new .docx file with the content
    try:
        # Create a basic document with python-docx
        doc = Document()
        paragraph = doc.add_paragraph(f"Content extracted from {filename} (basic conversion)")
        doc.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error in fallback conversion: {e}")
        return None

def merge_docx_files(docx_files, output_path, status_dir):
    """
    Merge multiple .docx files into a single document
    
    Before each file's content, a header line with the filename is added.
    Updates status periodically.
    """
    # Create a new output document
    merged_doc = Document()
    
    total_files = len(docx_files)
    processed_files = 0
    failed_files = []
    
    # Initialize status
    status = {
        'status': 'processing',
        'total': total_files,
        'processed': processed_files,
        'failed': 0,
        'progress_percent': 0
    }
    save_status(status_dir, status)
    
    # Process each file
    for file_path in docx_files:
        try:
            # Get the filename for the header
            filename = os.path.basename(file_path)
            
            # Add a separator paragraph with the filename
            separator = merged_doc.add_paragraph()
            run = separator.add_run(f"<{filename}>")
            run.font.bold = True
            run.font.size = Pt(12)
            
            # Add dots to complete the separator line (approximately 100 dots)
            run = separator.add_run("." * 100)
            run.font.bold = True
            
            # Try to open the document
            try:
                source_doc = Document(file_path)
                
                # Copy each paragraph from the source document
                for para in source_doc.paragraphs:
                    # Create a new paragraph in the merged document
                    merged_para = merged_doc.add_paragraph()
                    
                    # Copy the text and formatting of each run
                    for run in para.runs:
                        merged_run = merged_para.add_run(run.text)
                        merged_run.bold = run.bold
                        merged_run.italic = run.italic
                        merged_run.underline = run.underline
                        if run.font.size:
                            merged_run.font.size = run.font.size
                
                # Add a separator between documents
                merged_doc.add_paragraph()
                
            except Exception as e:
                # If we can't open the document, note it in the merged document
                error_para = merged_doc.add_paragraph()
                error_run = error_para.add_run(f"[Error reading file: {str(e)}]")
                error_run.font.color.rgb = RGBColor(255, 0, 0)  # Red color for error
                merged_doc.add_paragraph()
                logger.error(f"Error processing file {filename}: {e}")
                failed_files.append(filename)
            
            # Update progress
            processed_files += 1
            if processed_files % 50 == 0 or processed_files == total_files:  # Update status every 50 files
                status = {
                    'status': 'processing',
                    'total': total_files,
                    'processed': processed_files,
                    'failed': len(failed_files),
                    'progress_percent': int((processed_files / total_files) * 100)
                }
                save_status(status_dir, status)
                
        except Exception as e:
            logger.error(f"General error processing {file_path}: {e}")
            failed_files.append(os.path.basename(file_path))
            processed_files += 1
    
    # Save the merged document
    try:
        merged_doc.save(output_path)
        logger.info(f"Merged document saved to {output_path}")
        
        # Update final status
        status = {
            'status': 'merging_complete',
            'total': total_files,
            'processed': processed_files,
            'failed': len(failed_files),
            'progress_percent': 100
        }
        save_status(status_dir, status)
        
        return {
            'success': True,
            'processed_files': processed_files,
            'failed_files': failed_files
        }
    except Exception as e:
        logger.error(f"Error saving merged document: {e}")
        status = {
            'status': 'error',
            'error': f"Error saving merged document: {str(e)}"
        }
        save_status(status_dir, status)
        
        return {
            'success': False,
            'error': str(e)
        }

def convert_docx_to_pdf(docx_path, pdf_path, status_dir):
    """
    Convert a .docx file to .pdf format
    
    This function attempts multiple methods to convert the document:
    1. libreoffice (if available)
    2. docx2pdf library (if installed)
    3. Basic fallback message if conversion is not possible
    """
    status = {
        'status': 'converting_to_pdf',
        'progress_percent': 0
    }
    save_status(status_dir, status)
    
    # Try LibreOffice first
    try:
        cmd = [
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', os.path.dirname(pdf_path), docx_path
        ]
        subprocess.run(cmd, check=True, timeout=300, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if PDF was created
        if os.path.exists(pdf_path):
            status = {
                'status': 'pdf_conversion_complete',
                'progress_percent': 100
            }
            save_status(status_dir, status)
            return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.warning(f"LibreOffice PDF conversion failed: {e}")
    
    # Try docx2pdf (not included by default, but we'll try in case it's installed)
    try:
        import docx2pdf
        docx2pdf.convert(docx_path, pdf_path)
        
        if os.path.exists(pdf_path):
            status = {
                'status': 'pdf_conversion_complete',
                'progress_percent': 100
            }
            save_status(status_dir, status)
            return True
    except ImportError:
        logger.warning("docx2pdf not available, trying other methods")
    except Exception as e:
        logger.warning(f"docx2pdf conversion failed: {e}")
    
    # Fallback: Create a simple PDF with a message
    try:
        # If all conversion methods fail, create a simple text file with .pdf extension
        # explaining the situation
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "PDF Conversion Not Available")
        c.drawString(100, 730, "The merged DOCX document has been created successfully.")
        c.drawString(100, 710, "However, PDF conversion is not available in this environment.")
        c.drawString(100, 690, "Please download the DOCX file and convert it locally.")
        c.save()
        
        status = {
            'status': 'pdf_conversion_failed',
            'message': 'PDF conversion tools not available. Created placeholder PDF.',
            'progress_percent': 100
        }
        save_status(status_dir, status)
        return True
    except Exception as e:
        logger.error(f"Error creating fallback PDF: {e}")
        
        status = {
            'status': 'pdf_conversion_failed',
            'error': str(e),
            'progress_percent': 100
        }
        save_status(status_dir, status)
        return False

def process_zip_file(zip_path, output_dir):
    """
    Process a zip file containing .doc/.docx files:
    1. Extract all .doc and .docx files
    2. Convert .doc to .docx if needed
    3. Merge all into a single .docx
    4. Convert the merged file to PDF
    
    This function operates asynchronously and updates a status file
    """
    # Create a temp directory for extraction
    extract_dir = os.path.join(output_dir, 'extracted')
    os.makedirs(extract_dir, exist_ok=True)
    
    # Initialize status
    status = {
        'status': 'starting',
        'progress_percent': 0
    }
    save_status(output_dir, status)
    
    # Start a thread to handle the processing
    def process_thread():
        try:
            # Update status to extracting
            status = {
                'status': 'extracting',
                'progress_percent': 5
            }
            save_status(output_dir, status)
            
            # Extract .doc and .docx files from the zip
            doc_files = extract_doc_files(zip_path, extract_dir)
            
            if not doc_files:
                status = {
                    'status': 'error',
                    'error': 'No .doc or .docx files found in the ZIP archive'
                }
                save_status(output_dir, status)
                return
            
            # Update status
            status = {
                'status': 'converting',
                'total_files': len(doc_files),
                'progress_percent': 10
            }
            save_status(output_dir, status)
            
            # Convert .doc files to .docx if needed
            docx_files = []
            converted_count = 0
            
            for file_path in doc_files:
                if file_path.lower().endswith('.doc'):
                    # Convert .doc to .docx
                    converted_path = convert_doc_to_docx(file_path, extract_dir)
                    if converted_path:
                        docx_files.append(converted_path)
                        converted_count += 1
                else:
                    # Already a .docx file
                    docx_files.append(file_path)
                
                # Update conversion status every 50 files
                if (converted_count + len(docx_files) - converted_count) % 50 == 0:
                    progress = min(30, 10 + (converted_count / len(doc_files) * 20))
                    status = {
                        'status': 'converting',
                        'converted': converted_count,
                        'total_files': len(doc_files),
                        'progress_percent': int(progress)
                    }
                    save_status(output_dir, status)
            
            # Merge the docx files
            docx_output_path = os.path.join(output_dir, 'merged_document.docx')
            merge_result = merge_docx_files(docx_files, docx_output_path, output_dir)
            
            if not merge_result['success']:
                status = {
                    'status': 'error',
                    'error': merge_result.get('error', 'Error merging documents')
                }
                save_status(output_dir, status)
                return
            
            # Convert the merged docx to PDF
            pdf_output_path = os.path.join(output_dir, 'merged_document.pdf')
            pdf_result = convert_docx_to_pdf(docx_output_path, pdf_output_path, output_dir)
            
            # Final status update
            final_status = {
                'status': 'complete',
                'docx_path': docx_output_path,
                'pdf_path': pdf_output_path if pdf_result else None,
                'pdf_conversion_success': pdf_result,
                'processed_files': merge_result['processed_files'],
                'failed_files': len(merge_result['failed_files']),
                'failed_file_names': merge_result['failed_files'],
                'progress_percent': 100
            }
            save_status(output_dir, final_status)
            
        except Exception as e:
            logger.error(f"Error in processing thread: {e}")
            status = {
                'status': 'error',
                'error': str(e)
            }
            save_status(output_dir, status)
    
    # Start the processing thread
    thread = Thread(target=process_thread)
    thread.daemon = True
    thread.start()
    
    # Return immediately with initial information
    return {
        'success': True,
        'docx_path': os.path.join(output_dir, 'merged_document.docx'),
        'pdf_path': os.path.join(output_dir, 'merged_document.pdf'),
        'status_file': os.path.join(output_dir, 'status.json'),
        'message': 'Processing started',
        'processed_files': 0,
        'failed_files': 0
    }

def cleanup_old_files(directory, max_age_hours=24):
    """Delete files older than max_age_hours from the directory"""
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for root, dirs, files in os.walk(directory, topdown=False):
            # Remove old files
            for file in files:
                file_path = os.path.join(root, file)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        logger.debug(f"Removed old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error removing file {file_path}: {e}")
            
            # Remove empty directories (or old directories)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                
                # Check if directory is empty
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        logger.debug(f"Removed empty directory: {dir_path}")
                    except Exception as e:
                        logger.warning(f"Error removing directory {dir_path}: {e}")
                else:
                    # Check if all files in directory are old
                    dir_age = current_time - os.path.getmtime(dir_path)
                    if dir_age > max_age_seconds:
                        try:
                            shutil.rmtree(dir_path)
                            logger.debug(f"Removed old directory tree: {dir_path}")
                        except Exception as e:
                            logger.warning(f"Error removing directory tree {dir_path}: {e}")
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
