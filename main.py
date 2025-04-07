"""
DocxFilesMerger - Application de traitement et fusion de documents.
Version: CLI améliorée avec interface web minimale
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import sys
import os
import subprocess
from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory
import threading
import time

# Créer l'application Flask pour la démo en ligne
app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil avec informations sur l'outil CLI"""
    return render_template('index.html')

@app.route('/run_demo')
def run_demo():
    """Exécute la démo en arrière-plan et affiche le résultat"""
    # Démarrer un thread pour exécuter la démo
    thread = threading.Thread(target=run_demo_process)
    thread.daemon = True
    thread.start()
    
    # Rediriger vers la page des résultats
    return redirect(url_for('demo_results'))

def run_demo_process():
    """Exécute le processus de démo"""
    try:
        # Exécuter le script de démo
        subprocess.run([sys.executable, 'demo_cli.py'], 
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Erreur lors de l'exécution de la démo: {e}")

@app.route('/demo_results')
def demo_results():
    """Affiche les résultats de la démo"""
    return render_template('demo_results.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    """Télécharger un fichier résultant de la démo"""
    directory = os.path.dirname(filename)
    file = os.path.basename(filename)
    return send_from_directory(directory, file, as_attachment=True)

# Fonction principale
if __name__ == "__main__":
    # Si des arguments sont fournis, exécuter en mode CLI
    if len(sys.argv) > 1:
        from docx_merger_cli import main
        sys.exit(main())
    else:
        # Sinon, exécuter en mode web
        app.run(host="0.0.0.0", port=5000, debug=True)