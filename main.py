#!/usr/bin/env python3
"""
DocxFilesMerger - Application de traitement et fusion de documents.
Version: CLI pour Replit
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import sys
import os
import argparse
import logging
import subprocess
from flask import Flask, render_template_string, redirect, jsonify, send_from_directory, request, send_file
import threading
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('docx_merger')

# Créer l'application Flask
app = Flask(__name__)

# Template HTML simple
CLI_DOCS_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocxFilesMerger CLI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
            padding: 20px 0;
        }
        .container {
            max-width: 900px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
        }
        code {
            color: #d63384;
        }
        .icon-large {
            font-size: 3rem;
            color: #0d6efd;
        }
        .feature-card {
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .terminal {
            background-color: #212529;
            color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }
        .hidden {
            display: none;
        }
        .terminal p {
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }
        .demo-results {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="mb-4 text-center">
            <h1>DocxFilesMerger CLI</h1>
            <p class="lead">Outil de fusion de documents DOCX - Version ligne de commande</p>
        </header>
        
        <div class="alert alert-primary" role="alert">
            <i class="bi bi-info-circle-fill me-2"></i>
            <strong>Note:</strong> Cette application est maintenant disponible uniquement en ligne de commande.
        </div>

        <div class="row mb-4">
            <div class="col-md-4 mb-3">
                <div class="card h-100 feature-card">
                    <div class="card-body text-center">
                        <i class="bi bi-terminal icon-large mb-3"></i>
                        <h5 class="card-title">Accès en ligne de commande</h5>
                        <p class="card-text">Utilisez l'outil directement depuis le terminal pour une intégration facile dans des scripts.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card h-100 feature-card">
                    <div class="card-body text-center">
                        <i class="bi bi-file-earmark-zip icon-large mb-3"></i>
                        <h5 class="card-title">Traitement par lot</h5>
                        <p class="card-text">Traitez un ou plusieurs fichiers ZIP contenant des documents DOCX en une seule commande.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card h-100 feature-card">
                    <div class="card-body text-center">
                        <i class="bi bi-file-earmark-pdf icon-large mb-3"></i>
                        <h5 class="card-title">Conversion automatique</h5>
                        <p class="card-text">Fusionnez et convertissez automatiquement vos documents en DOCX et PDF.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card mb-4">
            <div class="card-header">
                <h5><i class="bi bi-book me-2"></i>Mode d'emploi</h5>
            </div>
            <div class="card-body">
                <h6>Syntaxe:</h6>
                <pre><code>python main.py [options]</code></pre>
                
                <h6 class="mt-3">Options:</h6>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Option</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>-f, --fichier FICHIER</code></td>
                            <td>Chemin vers un fichier ZIP à traiter</td>
                        </tr>
                        <tr>
                            <td><code>-d, --dossier DOSSIER</code></td>
                            <td>Chemin vers un dossier contenant des fichiers ZIP</td>
                        </tr>
                        <tr>
                            <td><code>-o, --output DOSSIER</code></td>
                            <td>Dossier de sortie (défaut: ./output)</td>
                        </tr>
                        <tr>
                            <td><code>-q, --quiet</code></td>
                            <td>Mode silencieux (sans affichage de progression)</td>
                        </tr>
                        <tr>
                            <td><code>-r, --rapport FICHIER</code></td>
                            <td>Générer un rapport CSV des résultats</td>
                        </tr>
                    </tbody>
                </table>
                
                <h6 class="mt-3">Exemples:</h6>
                <pre><code># Mode démo automatique (sans arguments)
python main.py

# Traiter un fichier spécifique
python main.py -f archive.zip -o ./resultats

# Traiter tous les fichiers d'un dossier
python main.py -d ./archives -o ./resultats -r rapport.csv</code></pre>

                <div class="alert alert-secondary mt-4">
                    <h6 class="mb-3"><i class="bi bi-terminal me-2"></i>Exécuter une démo</h6>
                    <p>Vous pouvez exécuter une démonstration directement depuis cette interface web:</p>
                    <button id="runDemoBtn" class="btn btn-primary">
                        <i class="bi bi-play-fill me-1"></i>
                        Lancer la démo
                    </button>
                    <div id="terminal" class="terminal hidden"></div>
                    <div id="demoResults" class="demo-results hidden">
                        <div class="alert alert-success">
                            <h6>Fichiers générés:</h6>
                            <ul id="filesList">
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="text-center text-muted mt-5">
            <p>Développé par MOA Digital Agency LLC | Copyright © 2025</p>
        </footer>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const runDemoBtn = document.getElementById('runDemoBtn');
            const terminal = document.getElementById('terminal');
            const demoResults = document.getElementById('demoResults');
            const filesList = document.getElementById('filesList');
            
            runDemoBtn.addEventListener('click', function() {
                // Réinitialiser l'interface
                terminal.innerHTML = '';
                terminal.classList.remove('hidden');
                demoResults.classList.add('hidden');
                filesList.innerHTML = '';
                
                // Désactiver le bouton pendant l'exécution
                runDemoBtn.disabled = true;
                runDemoBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exécution en cours...';
                
                // Envoyer la requête pour exécuter la démo
                fetch('/run_demo')
                .then(response => {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    function processStream({ done, value }) {
                        if (done) {
                            // Réactiver le bouton
                            runDemoBtn.disabled = false;
                            runDemoBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Lancer la démo';
                            
                            // Afficher les résultats
                            fetch('/demo_results')
                            .then(res => res.json())
                            .then(data => {
                                if (data.files && data.files.length > 0) {
                                    demoResults.classList.remove('hidden');
                                    
                                    data.files.forEach(file => {
                                        const li = document.createElement('li');
                                        li.innerHTML = `<a href="/download/${file.path}" target="_blank">${file.name}</a> (${file.type})`;
                                        filesList.appendChild(li);
                                    });
                                }
                            });
                            
                            return;
                        }
                        
                        // Ajouter le texte au terminal
                        const text = decoder.decode(value);
                        const lines = text.split('\n');
                        
                        lines.forEach(line => {
                            if (line.trim()) {
                                const p = document.createElement('p');
                                p.textContent = line;
                                terminal.appendChild(p);
                                terminal.scrollTop = terminal.scrollHeight;
                            }
                        });
                        
                        // Continuer à lire
                        return reader.read().then(processStream);
                    }
                    
                    return reader.read().then(processStream);
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    terminal.innerHTML += '<p style="color: red;">Erreur lors de l\'exécution de la démo.</p>';
                    runDemoBtn.disabled = false;
                    runDemoBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Lancer la démo';
                });
            });
        });
    </script>
</body>
</html>
"""

# Variables globales pour stocker l'état de la démo
demo_output = []
demo_results = {"files": []}
demo_running = False

# Afficher un message d'information
def show_header():
    print("\n" + "="*70)
    print("DocxFilesMerger CLI - Outil de traitement de documents".center(70))
    print("Développé par MOA Digital Agency LLC (https://myoneart.com)".center(70))
    print("Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.".center(70))
    print("="*70 + "\n")

def print_usage():
    """Affiche les informations d'utilisation"""
    print("UTILISATION:")
    print("  python main.py [options]")
    print("\nOPTIONS:")
    print("  -f, --fichier FICHIER     Chemin vers un fichier ZIP à traiter")
    print("  -d, --dossier DOSSIER     Chemin vers un dossier contenant des fichiers ZIP")
    print("  -o, --output DOSSIER      Dossier de sortie (défaut: ./output)")
    print("  -q, --quiet               Mode silencieux (sans affichage de progression)")
    print("  -r, --rapport FICHIER     Générer un rapport CSV des résultats")
    print("  -h, --help                Afficher ce message d'aide")
    print("\nEXEMPLES:")
    print("  # Mode démo automatique (sans arguments)")
    print("  python main.py")
    print("\n  # Traiter un fichier spécifique")
    print("  python main.py -f archive.zip -o ./resultats")
    print("\n  # Traiter tous les fichiers d'un dossier")
    print("  python main.py -d ./archives -o ./resultats -r rapport.csv")

# Capturer la sortie standard
class StdoutCapture:
    def __init__(self, callback):
        self.callback = callback
        self.original_stdout = sys.stdout
        
    def write(self, text):
        self.original_stdout.write(text)
        self.callback(text)
        
    def flush(self):
        self.original_stdout.flush()

# Fonction principale CLI
def cli_main():
    show_header()
    
    parser = argparse.ArgumentParser(add_help=False, description="Traitement et fusion de documents DOCX")
    
    parser.add_argument('-f', '--fichier', help='Chemin vers un fichier ZIP à traiter')
    parser.add_argument('-d', '--dossier', help='Chemin vers un dossier contenant des fichiers ZIP')
    parser.add_argument('-o', '--output', default='./output', help='Dossier de sortie')
    parser.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux')
    parser.add_argument('-r', '--rapport', help='Générer un rapport CSV des résultats')
    parser.add_argument('-h', '--help', action='store_true', help='Afficher ce message d\'aide')
    
    args, unknown = parser.parse_known_args()
    
    if args.help or (len(sys.argv) > 1 and all(arg.startswith('-h') or arg.startswith('--help') for arg in sys.argv[1:])):
        print_usage()
        return 0
    
    if len(sys.argv) <= 1:
        logger.info("Aucun argument fourni. Lancement du mode démonstration...")
        logger.info("Pour plus d'options, utilisez --help.\n")
        
        # Exécuter le script de démo
        from demo_cli import main as demo_main
        return demo_main()
    else:
        # Importer ici pour éviter de ralentir le démarrage
        from docx_merger_cli import traiter_fichier, traiter_dossier, generer_rapport
        
        resultats = []
        
        # Traiter un fichier unique
        if args.fichier:
            if not os.path.isfile(args.fichier):
                logger.error(f"Le fichier {args.fichier} n'existe pas.")
                return 1
                
            logger.info(f"Traitement du fichier: {args.fichier}")
            resultat = traiter_fichier(args.fichier, args.output, args.quiet)
            resultats.append(resultat)
            
        # Traiter un dossier
        elif args.dossier:
            if not os.path.isdir(args.dossier):
                logger.error(f"Le dossier {args.dossier} n'existe pas.")
                return 1
                
            logger.info(f"Traitement du dossier: {args.dossier}")
            resultats = traiter_dossier(args.dossier, args.output, args.quiet)
            
        # Générer un rapport si demandé
        if args.rapport and resultats:
            generer_rapport(resultats, args.rapport)
            logger.info(f"Rapport généré: {args.rapport}")
        
        return 0

@app.route('/')
def home():
    """Page d'accueil avec documentation CLI"""
    return render_template_string(CLI_DOCS_TEMPLATE)

@app.route('/run_demo')
def run_demo():
    """Exécuter le script de démonstration et streamer la sortie"""
    global demo_output, demo_results, demo_running
    
    def run_demo_task():
        global demo_output, demo_results, demo_running
        
        demo_running = True
        demo_output = []
        demo_results = {"files": []}
        
        # Capturer la sortie standard
        def capture_output(text):
            demo_output.append(text)
            
        sys.stdout = StdoutCapture(capture_output)
        
        try:
            # Créer le dossier de sortie pour la démo
            demo_dir = "test_demo"
            if not os.path.exists(demo_dir):
                os.makedirs(demo_dir)
                
            # Exécuter la démo
            from demo_cli import main as demo_main
            demo_main()
            
            # Ajouter les fichiers générés aux résultats
            docx_path = os.path.join(demo_dir, "resultats", "merged.docx")
            pdf_path = os.path.join(demo_dir, "resultats", "merged.pdf")
            
            if os.path.exists(docx_path):
                demo_results["files"].append({
                    "name": "Document fusionné (DOCX)",
                    "path": "test_demo/resultats/merged.docx",
                    "type": "DOCX"
                })
                
            if os.path.exists(pdf_path):
                demo_results["files"].append({
                    "name": "Document fusionné (PDF)",
                    "path": "test_demo/resultats/merged.pdf",
                    "type": "PDF"
                })
                
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la démo: {str(e)}")
            demo_output.append(f"Erreur: {str(e)}")
        
        # Restaurer la sortie standard
        sys.stdout = sys.__stdout__
        demo_running = False
    
    # Lancer la tâche dans un thread
    thread = threading.Thread(target=run_demo_task)
    thread.daemon = True
    thread.start()
    
    # Stream la sortie au client
    def generate():
        global demo_output, demo_running
        
        last_index = 0
        while demo_running or last_index < len(demo_output):
            if last_index < len(demo_output):
                yield ''.join(demo_output[last_index:])
                last_index = len(demo_output)
            else:
                import time
                time.sleep(0.1)
    
    return app.response_class(generate(), mimetype='text/plain')

@app.route('/demo_results')
def get_demo_results():
    """Récupérer les résultats de la démo"""
    global demo_results
    return jsonify(demo_results)

@app.route('/download/<path:file_path>')
def download_file(file_path):
    """Télécharger un fichier généré par la démo"""
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir les fichiers statiques"""
    return send_from_directory('static', filename)

@app.route('/<path:path>')
def catch_all(path):
    """Rediriger toutes les autres routes vers la page d'accueil"""
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    """Gérer les erreurs 404"""
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    """Gérer les erreurs 500"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erreur serveur</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="text-center">
                <h1 class="text-danger">Erreur serveur</h1>
                <p class="lead">Une erreur s'est produite sur le serveur.</p>
                <a href="/" class="btn btn-primary">Retour à l'accueil</a>
            </div>
        </div>
    </body>
    </html>
    """), 500

# Point d'entrée principal pour ligne de commande
def main_cli():
    sys.exit(cli_main())

# Point d'entrée principal
if __name__ == "__main__":
    # Si exécuté directement, lancer le CLI
    if len(sys.argv) > 1:
        sys.exit(cli_main())
    else:
        # Sinon, démarrer l'application web
        app.run(host="0.0.0.0", port=5000, debug=True)