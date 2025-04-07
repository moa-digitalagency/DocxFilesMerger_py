"""
DocxFilesMerger - Application de traitement et fusion de documents.
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

import os
from flask import Flask
from models import db
from app import app as flask_app

# S'assurer que l'application a une URI de base de données
if 'SQLALCHEMY_DATABASE_URI' not in flask_app.config and os.environ.get('DATABASE_URL'):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# Initialiser la base de données
with flask_app.app_context():
    db.create_all()

app = flask_app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
