"""
DocxFilesMerger - Application de traitement et fusion de documents.
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import os
import json
import time
import zipfile
import threading
import shutil
import tempfile
import glob
from docx import Document
import traceback
from datetime import datetime, timedelta

def save_status(status_dir, status_data):
    """Save processing status to a JSON file"""
    try:
        status_file = os.path.join(status_dir, 'status.json')
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    except Exception as e:
        print(f"Error saving status: {str(e)}")

def extract_doc_files(zip_path, extract_dir):
    """Extract all .doc and .docx files from a zip file"""
    doc_files = []
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # List all files in the ZIP
        all_files = zip_ref.namelist()
        
        # Filter for .doc and .docx files
        doc_files_in_zip = [f for f in all_files if f.lower().endswith(('.doc', '.docx'))]
        
        # Extract only document files
        for file in doc_files_in_zip:
            # Create necessary directories
            file_path = os.path.join(extract_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Extract file
            with zip_ref.open(file) as source, open(file_path, 'wb') as target:
                shutil.copyfileobj(source, target)
            
            doc_files.append(file_path)
    
    return doc_files

def convert_doc_to_docx(doc_path, output_dir):
    """
    Convert a .doc file to .docx format
    
    This function attempts to use LibreOffice for conversion if available,
    falling back to a basic document creation method if not
    """
    if not doc_path.lower().endswith('.doc'):
        return doc_path  # Already a .docx or other format
    
    filename = os.path.basename(doc_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(output_dir, f"{name_without_ext}.docx")
    
    try:
        # Try to use LibreOffice (if installed)
        libreoffice_path = shutil.which('libreoffice')
        if libreoffice_path:
            os.system(f'"{libreoffice_path}" --headless --convert-to docx --outdir "{output_dir}" "{doc_path}"')
            
            if os.path.exists(output_path):
                return output_path
        
        # Try to use docx2pdf's converter (which can sometimes convert doc to docx)
        try:
            from docx2pdf import convert
            convert(doc_path, output_path)
            if os.path.exists(output_path):
                return output_path
        except:
            pass
        
        # Fallback: Create a new .docx document with a message
        doc = Document()
        doc.add_paragraph(f"Impossible de convertir le document '{filename}'. Le format .doc original n'est pas entièrement pris en charge.")
        doc.save(output_path)
        return output_path
        
    except Exception as e:
        print(f"Error converting {doc_path} to .docx: {str(e)}")
        
        # Create an error document as a last resort
        try:
            doc = Document()
            doc.add_paragraph(f"Erreur lors de la conversion du document '{filename}': {str(e)}")
            doc.save(output_path)
            return output_path
        except:
            return doc_path  # Just return the original in case of severe failure

def merge_docx_files(docx_files, output_path, status_dir):
    """
    Merge multiple .docx files into a single document
    
    Before each file's content, a header line with the filename is added.
    Updates status periodically.
    """
    # Create a new merged document
    merged_doc = Document()
    total_files = len(docx_files)
    processed_files = 0
    
    for file_path in sorted(docx_files):
        try:
            # Update status (for UX)
            processed_files += 1
            percent_complete = int((processed_files / total_files) * 100)
            save_status(status_dir, {
                'percent': 50 + int(percent_complete / 2),  # 50-75% progress
                'status_text': f'Fusion du document {processed_files}/{total_files}',
                'current_step': 'merge',
                'complete': False,
                'file_count': total_files
            })
            
            # Add a separator with the filename
            filename = os.path.basename(file_path)
            merged_doc.add_paragraph(f"{'='*50}\n<{filename}>\n{'='*50}")
            
            # Open the source document
            try:
                source_doc = Document(file_path)
                
                # Copy all paragraphs from source to merged document
                for paragraph in source_doc.paragraphs:
                    text = paragraph.text
                    p = merged_doc.add_paragraph(text)
                    
                # Add a page break after each document except the last one
                if processed_files < total_files:
                    merged_doc.add_page_break()
                    
            except Exception as e:
                # If we can't open a specific document, add an error message
                merged_doc.add_paragraph(f"Impossible d'ouvrir ce document: {str(e)}")
                merged_doc.add_page_break()
                
        except Exception as e:
            print(f"Error merging file {file_path}: {str(e)}")
    
    # Save the merged document
    try:
        merged_doc.save(output_path)
        return output_path
    except Exception as e:
        error_msg = f"Failed to save merged document: {str(e)}"
        print(error_msg)
        save_status(status_dir, {
            'percent': 75,
            'status_text': 'Erreur lors de la sauvegarde du document fusionné',
            'current_step': 'merge',
            'complete': False,
            'error': error_msg
        })
        raise Exception(error_msg)

def convert_docx_to_pdf(docx_path, pdf_path, status_dir):
    """
    Convert a .docx file to .pdf format
    
    This function attempts multiple methods to convert the document:
    1. libreoffice (if available)
    2. docx2pdf library (if installed)
    3. Basic fallback message if conversion is not possible
    """
    save_status(status_dir, {
        'percent': 80,
        'status_text': 'Conversion du document fusionné en PDF...',
        'current_step': 'pdf',
        'complete': False
    })
    
    conversion_successful = False
    error_message = ""
    
    # Method 1: Try LibreOffice
    try:
        libreoffice_path = shutil.which('libreoffice')
        if libreoffice_path:
            output_dir = os.path.dirname(pdf_path)
            os.system(f'"{libreoffice_path}" --headless --convert-to pdf --outdir "{output_dir}" "{docx_path}"')
            
            # Check if the conversion was successful
            temp_pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(docx_path))[0] + '.pdf')
            if os.path.exists(temp_pdf_path):
                # Move to the desired location if needed
                if temp_pdf_path != pdf_path:
                    shutil.move(temp_pdf_path, pdf_path)
                conversion_successful = True
    except Exception as e:
        error_message += f"LibreOffice method failed: {str(e)}\n"
    
    # Method 2: Try docx2pdf
    if not conversion_successful:
        try:
            from docx2pdf import convert
            convert(docx_path, pdf_path)
            
            if os.path.exists(pdf_path):
                conversion_successful = True
        except Exception as e:
            error_message += f"docx2pdf method failed: {str(e)}\n"
    
    # Method 3: Try using ReportLab as fallback
    if not conversion_successful:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            document = Document(docx_path)
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            y = height - 40
            
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 20, "Aperçu du document (conversion limitée)")
            
            # Add a note that full conversion wasn't possible
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Document PDF (aperçu simplifié)")
            y -= 20
            
            c.setFont("Helvetica", 10)
            c.drawString(40, y, "La conversion complète du document DOCX en PDF n'a pas été possible.")
            y -= 12
            c.drawString(40, y, "Veuillez télécharger le fichier DOCX pour une visualisation complète.")
            y -= 30
            
            # Try to include some of the text content
            c.setFont("Helvetica", 10)
            for para in document.paragraphs:
                if not para.text.strip():
                    continue
                    
                text = para.text
                # Split long lines
                while len(text) > 0:
                    if len(text) > 90:
                        split_point = text.rfind(' ', 0, 90)
                        if split_point == -1:  # No space found
                            split_point = 90
                        line = text[:split_point]
                        text = text[split_point:].strip()
                    else:
                        line = text
                        text = ""
                    
                    c.drawString(40, y, line)
                    y -= 12
                    
                    # New page if needed
                    if y < 40:
                        c.showPage()
                        y = height - 40
                
                # Add some space between paragraphs
                y -= 6
                
                # New page if needed
                if y < 40:
                    c.showPage()
                    y = height - 40
            
            c.save()
            conversion_successful = True
        except Exception as e:
            error_message += f"ReportLab method failed: {str(e)}\n"
    
    # If all methods failed, create a simple PDF with error message
    if not conversion_successful:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(40, height - 40, "Erreur de conversion PDF")
            
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 80, "La conversion du document DOCX en PDF a échoué.")
            c.drawString(40, height - 100, "Veuillez télécharger le fichier DOCX à la place.")
            c.drawString(40, height - 140, "Détails de l'erreur:")
            
            # Print error message
            y = height - 160
            for i, line in enumerate(error_message.split('\n')):
                if line:
                    c.drawString(60, y - (i * 15), line[:80])  # Limit line length
            
            c.save()
        except Exception as e:
            print(f"Failed to create error PDF: {str(e)}")
            return None
    
    return pdf_path

def process_zip_file(zip_path, output_dir, status_dir=None):
    """
    Process a zip file containing .doc/.docx files:
    1. Extract all .doc and .docx files
    2. Convert .doc to .docx if needed
    3. Merge all into a single .docx
    4. Convert the merged file to PDF
    
    This function operates asynchronously and updates a status file
    """
    if status_dir is None:
        status_dir = output_dir
        
    extract_dir = os.path.join(output_dir, 'extracted')
    converted_dir = os.path.join(output_dir, 'converted')
    merged_docx_path = os.path.join(output_dir, 'merged.docx')
    merged_pdf_path = os.path.join(output_dir, 'merged.pdf')
    
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)
    
    start_time = int(time.time())
    
    def process_thread():
        try:
            # 1. Extract files
            save_status(status_dir, {
                'percent': 10,
                'status_text': 'Extraction des fichiers du ZIP...',
                'current_step': 'extract',
                'complete': False,
                'start_time': start_time
            })
            
            doc_files = extract_doc_files(zip_path, extract_dir)
            file_count = len(doc_files)
            
            save_status(status_dir, {
                'percent': 30,
                'status_text': f'{file_count} fichiers extraits.',
                'current_step': 'extract',
                'complete': False,
                'file_count': file_count,
                'start_time': start_time
            })
            
            if not doc_files:
                raise Exception("Aucun fichier .doc ou .docx trouvé dans l'archive ZIP.")
            
            # 2. Convert .doc to .docx
            save_status(status_dir, {
                'percent': 40,
                'status_text': 'Conversion des fichiers .doc en .docx...',
                'current_step': 'convert',
                'complete': False,
                'file_count': file_count,
                'start_time': start_time
            })
            
            converted_files = []
            for i, doc_path in enumerate(doc_files):
                if i % max(1, int(file_count / 10)) == 0:  # Update status every ~10% of files
                    percent = 40 + int((i / file_count) * 10)
                    save_status(status_dir, {
                        'percent': percent,
                        'status_text': f'Conversion des fichiers ({i}/{file_count})...',
                        'current_step': 'convert',
                        'complete': False,
                        'file_count': file_count,
                        'start_time': start_time
                    })
                
                if doc_path.lower().endswith('.doc'):
                    converted_path = convert_doc_to_docx(doc_path, converted_dir)
                    converted_files.append(converted_path)
                else:
                    # Copy the .docx file to the converted directory
                    filename = os.path.basename(doc_path)
                    converted_path = os.path.join(converted_dir, filename)
                    shutil.copy2(doc_path, converted_path)
                    converted_files.append(converted_path)
            
            # 3. Merge all .docx files
            save_status(status_dir, {
                'percent': 50,
                'status_text': 'Fusion des documents en un seul fichier...',
                'current_step': 'merge',
                'complete': False,
                'file_count': file_count,
                'start_time': start_time
            })
            
            merge_docx_files(converted_files, merged_docx_path, status_dir)
            
            # 4. Convert merged file to PDF
            convert_docx_to_pdf(merged_docx_path, merged_pdf_path, status_dir)
            
            # 5. Completed
            end_time = int(time.time())
            save_status(status_dir, {
                'percent': 100,
                'status_text': 'Traitement terminé avec succès !',
                'current_step': 'complete',
                'complete': True,
                'file_count': file_count,
                'start_time': start_time,
                'end_time': end_time
            })
            
        except Exception as e:
            error_message = str(e)
            error_traceback = traceback.format_exc()
            print(f"Error processing ZIP file: {error_message}")
            print(error_traceback)
            
            save_status(status_dir, {
                'percent': 0,
                'status_text': 'Une erreur s\'est produite.',
                'current_step': 'error',
                'complete': False,
                'error': error_message,
                'traceback': error_traceback,
                'start_time': start_time,
                'end_time': int(time.time())
            })
    
    # Start processing in a thread
    thread = threading.Thread(target=process_thread)
    thread.daemon = True
    thread.start()
    
    return thread

def cleanup_old_files(directory, max_age_hours=24):
    """Delete files older than max_age_hours from the directory"""
    current_time = datetime.now()
    
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Skip if it's not a directory or file
            if not os.path.isdir(item_path) and not os.path.isfile(item_path):
                continue
                
            # Get the modification time
            mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
            
            # Check if the file/directory is older than max_age_hours
            if current_time - mod_time > timedelta(hours=max_age_hours):
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    os.remove(item_path)
                    
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
