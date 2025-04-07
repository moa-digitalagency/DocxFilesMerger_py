#!/usr/bin/env python3
"""
DocxFilesMerger - Serveur Web pour la documentation CLI
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

from flask import Flask, render_template_string, redirect, jsonify, send_from_directory
import os
import subprocess

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
                    <p>Vous pouvez exécuter une démonstration avec la commande: <code>python main.py</code></p>
                    <a href="/run_demo" class="btn btn-primary">
                        <i class="bi bi-play-fill me-1"></i>
                        Lancer la démo en arrière-plan
                    </a>
                </div>
            </div>
        </div>
        
        <footer class="text-center text-muted mt-5">
            <p>Développé par MOA Digital Agency LLC | Copyright © 2025</p>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Page d'accueil avec documentation CLI"""
    return render_template_string(CLI_DOCS_TEMPLATE)

@app.route('/run_demo')
def run_demo():
    """Exécuter le script de démonstration en arrière-plan"""
    try:
        # Lancer le script de démo en arrière-plan
        subprocess.Popen(["python", "main.py"], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        return jsonify({
            "status": "success",
            "message": "La démo a été lancée en arrière-plan. Vérifiez la console pour les résultats."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du lancement de la démo: {str(e)}"
        })

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

# Servir l'application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)