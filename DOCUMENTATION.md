# Documentation: DocxFilesMerger CLI

## Présentation

DocxFilesMerger CLI est un outil en ligne de commande conçu pour simplifier le traitement des documents médicaux au format DOC/DOCX contenus dans des archives ZIP. Il permet d'automatiser plusieurs tâches courantes:

1. Extraire tous les documents DOC/DOCX d'une archive ZIP
2. Convertir les fichiers DOC au format DOCX si nécessaire
3. Fusionner tous les documents en un seul fichier DOCX unifié
4. Créer une version PDF du document fusionné

## Utilisation

### Commande de base

```bash
python docx_files_merger.py chemin/vers/archive.zip
```

Par défaut, les fichiers générés seront placés dans un dossier `./output`.

### Options disponibles

```bash
python docx_files_merger.py chemin/vers/archive.zip [options]
```

- `-o, --output-dir DOSSIER` : Spécifie le dossier de sortie (par défaut: `./output`)
- `-q, --quiet` : Mode silencieux, sans affichage des barres de progression
- `-h, --help` : Affiche l'aide et les informations d'utilisation

### Exemples

```bash
# Traitement basique
python docx_files_merger.py dossiers_medicaux.zip

# Spécifier un dossier de sortie
python docx_files_merger.py dossiers_medicaux.zip -o ./resultats_patient

# Mode silencieux
python docx_files_merger.py dossiers_medicaux.zip -q
```

## Utilisation comme bibliothèque Python

DocxFilesMerger peut également être utilisé comme module dans vos propres scripts Python:

```python
from docx_files_merger import process_zip_file

# Traiter une archive ZIP
docx_path, pdf_path = process_zip_file("archive.zip", "./resultats")

print(f"Document DOCX généré: {docx_path}")
print(f"Document PDF généré: {pdf_path}")
```

## Structure des fichiers générés

Lors du traitement d'une archive ZIP `archive.zip`, l'outil créera la structure suivante:

```
output/                    # Dossier de sortie principal
├── extracted/             # Contient les fichiers extraits
│   ├── document1.docx
│   ├── document2.docx
│   └── ...
├── merged.docx            # Document DOCX fusionné
└── merged.pdf             # Version PDF du document fusionné
```

## Résolution des problèmes

### Erreur: "Aucun fichier DOC/DOCX trouvé dans l'archive"

Vérifiez que votre archive ZIP contient bien des fichiers avec les extensions `.doc` ou `.docx`. L'outil ignore les autres types de fichiers.

### Erreur lors de la conversion PDF

La conversion en PDF peut utiliser trois méthodes différentes, en fonction des outils disponibles:

1. LibreOffice (méthode recommandée pour la meilleure qualité)
2. Bibliothèque docx2pdf 
3. Conversion basique avec reportlab

Si le fichier PDF généré est de qualité insuffisante, envisagez d'installer LibreOffice sur votre système.

## Traitements par lots

Pour traiter plusieurs archives ZIP en une seule opération, consultez l'exemple dans le fichier `exemple_utilisation.py`:

```python
from docx_files_merger import process_zip_file
import os
import glob

# Traiter tous les fichiers ZIP d'un dossier
zip_files = glob.glob("./dossier_archives/*.zip")
for zip_file in zip_files:
    base_name = os.path.basename(zip_file).split('.')[0]
    output_dir = f"./resultats/{base_name}"
    process_zip_file(zip_file, output_dir)
```

---

Pour une documentation technique plus complète, consultez le fichier `DOCUMENTATION_COMPLETE.md`.
