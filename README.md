# DocxFilesMerger CLI

Un outil en ligne de commande pour fusionner et convertir des documents médicaux à partir d'archives ZIP.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-proprietary-red)

## 📋 Fonctionnalités

- ✅ Extraction automatique des fichiers DOC/DOCX d'une archive ZIP
- ✅ Conversion des fichiers DOC au format DOCX
- ✅ Fusion de tous les documents en un seul fichier DOCX unifié
- ✅ Génération automatique d'une version PDF du document fusionné
- ✅ Barre de progression pour suivre l'avancement du traitement
- ✅ Traitement de fichiers individuels ou de dossiers entiers
- ✅ Génération de rapports CSV des résultats
- ✅ Interface en ligne de commande simple et efficace
- ✅ Mode démo automatique pour tester l'outil sans arguments

## 🚀 Installation

1. Assurez-vous d'avoir Python 3.8 ou supérieur installé
2. Clonez ce dépôt ou téléchargez les fichiers
3. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

4. Pour une conversion optimale vers PDF, installez LibreOffice (optionnel)

## 🔧 Utilisation

### Mode démo automatique (sans arguments)

```bash
python main.py
```

Ce mode crée automatiquement des fichiers de test, les place dans une archive ZIP, puis les traite pour vous montrer comment fonctionne l'outil.

### Traiter un seul fichier ZIP

```bash
python main.py -f chemin/vers/archive.zip -o ./resultats
```

### Traiter tous les fichiers ZIP d'un dossier

```bash
python main.py -d chemin/vers/dossier -o ./resultats
```

### Script d'exécution rapide (Unix/Linux/macOS)

```bash
./start_cli.sh -f archive.zip -o ./resultats
```

## 🛠️ Options disponibles

| Option | Description |
|--------|-------------|
| `-f, --fichier FICHIER` | Traiter un seul fichier ZIP |
| `-d, --dossier DOSSIER` | Traiter tous les fichiers ZIP d'un dossier |
| `-o, --output DOSSIER` | Dossier de sortie pour les résultats (défaut: ./output) |
| `-q, --quiet` | Mode silencieux, sans affichage des barres de progression |
| `-r, --rapport FICHIER` | Générer un rapport CSV des résultats de traitement |
| `-h, --help` | Afficher l'aide complète |

## 📝 Exemples d'utilisation

### Traiter un fichier et générer un rapport

```bash
python main.py -f archive.zip -o ./resultats -r rapport.csv
```

### Traiter tous les fichiers d'un dossier en mode silencieux

```bash
python main.py -d ./dossier_archives -o ./resultats -q
```

## 📚 Utilisation comme bibliothèque Python

Vous pouvez également utiliser DocxFilesMerger comme une bibliothèque dans vos propres scripts.

```python
from docx_merger_cli import traiter_fichier, traiter_dossier

# Traiter un fichier ZIP
resultat = traiter_fichier("chemin/vers/archive.zip", "./resultats")

# Traiter un dossier de fichiers ZIP
resultats = traiter_dossier("chemin/vers/dossier", "./resultats")

# Vérifier les résultats
if resultat["statut"] == "succès":
    print(f"Document fusionné : {resultat['docx']}")
    print(f"PDF généré : {resultat['pdf']}")
```

Voir `exemple_utilisation.py` pour un exemple complet.

## 📦 Structure du projet

- `main.py` - Point d'entrée principal et interface CLI
- `docx_merger_cli.py` - Fonctions principales de traitement
- `docx_files_merger.py` - Module de base pour la fusion de documents
- `demo_cli.py` - Script de démonstration automatique
- `exemple_utilisation.py` - Exemple d'utilisation comme bibliothèque
- `utils.py` - Fonctions utilitaires diverses

---

Développé par MOA Digital Agency LLC (https://myoneart.com)  
Email: moa@myoneart.com  
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
