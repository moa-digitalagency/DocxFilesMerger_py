# DocxFilesMerger CLI

Un outil en ligne de commande pour fusionner des documents médicaux à partir d'archives ZIP.

## Fonctionnalités

- Extraction automatique des fichiers DOC/DOCX d'une archive ZIP
- Conversion des fichiers DOC au format DOCX
- Fusion de tous les documents en un seul fichier DOCX unifié
- Génération automatique d'une version PDF du document fusionné
- Barre de progression pour suivre l'avancement du traitement
- Options de ligne de commande flexibles

## Installation

1. Assurez-vous d'avoir Python 3.8 ou supérieur installé
2. Installez les dépendances requises
3. Pour une meilleure expérience, installez les dépendances optionnelles
4. Pour une conversion optimale, installez LibreOffice

## Utilisation

```bash
python docx_files_merger.py chemin/vers/archive.zip
```

Options disponibles:
- `-o, --output-dir DOSSIER` : Spécifie le dossier de sortie (par défaut: `./output`)
- `-q, --quiet` : Mode silencieux, sans affichage des barres de progression

## Documentation

Pour une documentation plus détaillée, consultez:
- [Documentation d'utilisation](DOCUMENTATION.md)
- [Documentation technique complète](DOCUMENTATION_COMPLETE.md)
- [Guide de déploiement](DEPLOY.md)

---

Développé par MOA Digital Agency LLC (https://myoneart.com)  
Email: moa@myoneart.com  
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
