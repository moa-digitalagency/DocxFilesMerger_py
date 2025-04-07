"""
DocxFilesMerger - Application de traitement et fusion de documents.
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

# Ce fichier est utilisé seulement pour la compatibilité avec Replit.
# Pour utiliser l'outil, exécutez directement docx_files_merger.py

import sys
import os

# Afficher un message d'information
print("DocxFilesMerger CLI - Outil de fusion de documents")
print("Développé par MOA Digital Agency LLC (https://myoneart.com)")
print("Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.\n")

print("Pour utiliser cet outil:")
print("./docx_files_merger.py chemin/vers/archive.zip [options]\n")

print("Options disponibles:")
print("  -o, --output-dir DOSSIER : Dossier de sortie")
print("  -q, --quiet : Mode silencieux")
print("  -h, --help : Afficher l'aide\n")

print("Exemple d'utilisation:")
print("  ./docx_files_merger.py ./test_docx_merger/archive_test.zip -o ./resultats\n")

print("Documentation complète disponible dans DOCUMENTATION.md")

# Vérifier si des arguments sont passés et exécuter le script principal si nécessaire
if len(sys.argv) > 1:
    print("\nExécution de docx_files_merger.py avec vos arguments...\n")
    from docx_files_merger import main
    sys.exit(main())