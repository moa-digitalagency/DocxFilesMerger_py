#!/bin/bash
# Script pour exécuter DocxFilesMerger CLI
# Ce script lance l'application en ligne de commande

echo "Démarrage de DocxFilesMerger CLI..."
cd "$(dirname "$0")"

# Passer les arguments reçus à l'application
python main.py "$@"