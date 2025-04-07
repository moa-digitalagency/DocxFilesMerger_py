"""
DocxFilesMerger - Application de traitement et fusion de documents.
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import os
import time
import json
import shutil
import threading
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, abort
from utils import process_zip_file, cleanup_old_files

# Configuration de l'application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 500  # 500 MB
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.getcwd(), 'outputs')
app.config['STATUS_FOLDER'] = os.path.join(os.getcwd(), 'status')
app.config['ALLOWED_EXTENSIONS'] = {'zip'}

# Créer les dossiers nécessaires s'ils n'existent pas
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['STATUS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Vérification des extensions de fichiers autorisées
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route principale
@app.route('/')
def index():
    # Nettoyer les anciens fichiers à chaque rechargement de la page principale
    cleanup_thread = threading.Thread(target=cleanup_old_files, args=(app.config['UPLOAD_FOLDER'],))
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    cleanup_thread = threading.Thread(target=cleanup_old_files, args=(app.config['OUTPUT_FOLDER'],))
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    cleanup_thread = threading.Thread(target=cleanup_old_files, args=(app.config['STATUS_FOLDER'],))
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    return render_template('index.html')

# Route pour le téléversement du fichier
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier n\'a été téléversé.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Aucun fichier n\'a été sélectionné.'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Seuls les fichiers ZIP sont autorisés.'}), 400
    
    try:
        # Sécuriser le nom du fichier et créer un identifiant unique
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_folder = f"{timestamp}_{os.urandom(4).hex()}"
        
        # Créer un dossier spécifique pour cette session
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], unique_folder)
        status_folder = os.path.join(app.config['STATUS_FOLDER'], unique_folder)
        
        os.makedirs(session_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(status_folder, exist_ok=True)
        
        # Sauvegarder le fichier
        zip_path = os.path.join(session_folder, filename)
        file.save(zip_path)
        
        # Initialiser le statut
        status_file = os.path.join(status_folder, 'status.json')
        with open(status_file, 'w') as f:
            json.dump({
                'percent': 0,
                'status_text': 'Fichier téléversé avec succès.',
                'current_step': 'extract',
                'complete': False,
                'error': None,
                'start_time': timestamp
            }, f)
        
        # Estimer le nombre de fichiers (pour l'interface utilisateur)
        file_count = 20  # Valeur par défaut
        
        return jsonify({
            'success': True,
            'zip_path': zip_path,
            'output_dir': output_folder,
            'status_dir': status_folder,
            'file_count': file_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route pour traiter le fichier téléversé
@app.route('/process', methods=['POST'])
def process_file():
    data = request.json
    
    if not data or 'zip_path' not in data:
        return jsonify({'success': False, 'error': 'Données invalides.'}), 400
    
    zip_path = data['zip_path']
    
    if not os.path.exists(zip_path):
        return jsonify({'success': False, 'error': 'Le fichier ZIP n\'existe pas.'}), 404
    
    # Obtenir le dossier unique
    unique_folder = os.path.dirname(zip_path).split(os.path.sep)[-1]
    output_folder = os.path.join(app.config['OUTPUT_FOLDER'], unique_folder)
    status_folder = os.path.join(app.config['STATUS_FOLDER'], unique_folder)
    
    try:
        # Lancer le traitement dans un thread séparé
        process_thread = threading.Thread(
            target=process_zip_file,
            args=(zip_path, output_folder),
            kwargs={'status_dir': status_folder}
        )
        process_thread.daemon = True
        process_thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        # Enregistrer l'erreur dans le fichier de statut
        status_file = os.path.join(status_folder, 'status.json')
        with open(status_file, 'w') as f:
            json.dump({
                'percent': 0,
                'status_text': 'Une erreur s\'est produite.',
                'current_step': 'error',
                'complete': False,
                'error': str(e)
            }, f)
        
        return jsonify({'success': False, 'error': str(e)}), 500

# Route pour télécharger les fichiers traités
@app.route('/download/<file_type>')
def download_file(file_type):
    # Trouver le dossier de sortie le plus récent
    output_folders = [os.path.join(app.config['OUTPUT_FOLDER'], f) for f in os.listdir(app.config['OUTPUT_FOLDER'])]
    if not output_folders:
        abort(404)
    
    latest_folder = max(output_folders, key=os.path.getmtime)
    
    if file_type == 'docx':
        file_path = os.path.join(latest_folder, 'merged.docx')
        filename = 'documents_fusionnes.docx'
    elif file_type == 'pdf':
        file_path = os.path.join(latest_folder, 'merged.pdf')
        filename = 'documents_fusionnes.pdf'
    else:
        abort(404)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, as_attachment=True, download_name=filename)

# Route pour vérifier le statut du traitement
@app.route('/status')
def processing_status():
    # Trouver le dossier de statut le plus récent
    status_folders = [os.path.join(app.config['STATUS_FOLDER'], f) for f in os.listdir(app.config['STATUS_FOLDER'])]
    if not status_folders:
        return jsonify({'error': 'Aucun traitement en cours.'})
    
    latest_folder = max(status_folders, key=os.path.getmtime)
    status_file = os.path.join(latest_folder, 'status.json')
    
    if not os.path.exists(status_file):
        return jsonify({'error': 'Fichier de statut introuvable.'})
    
    try:
        with open(status_file, 'r') as f:
            status_data = json.load(f)
        
        # Ajouter des statistiques si le traitement est terminé
        if status_data.get('complete', False):
            start_time = status_data.get('start_time', 0)
            end_time = status_data.get('end_time', int(time.time()))
            processing_time = end_time - start_time
            
            status_data['stats'] = {
                'processing_time': processing_time,
                'file_count': status_data.get('file_count', 0)
            }
        
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la lecture du statut: {str(e)}'})

# Afficher le README
@app.route('/readme')
def show_readme():
    with open('README.md', 'r') as f:
        readme_content = f.read()
    
    # Ici, on pourrait convertir le Markdown en HTML pour un affichage plus élégant
    # Pour l'instant, on redirige simplement vers la page d'accueil
    return redirect(url_for('index'))

# Gestionnaire d'erreur 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page introuvable"), 404

# Gestionnaire d'erreur 500
@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Erreur interne du serveur"), 500

# Exécution de l'application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
