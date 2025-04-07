# Documentation de DocxFilesMerger

## Vue d'ensemble

DocxFilesMerger est un outil en ligne de commande pour traiter des documents médicaux à partir d'archives ZIP. L'outil permet d'extraire, convertir, et fusionner des fichiers DOC et DOCX, puis de générer un PDF du document fusionné.

## Architecture

L'application est structurée autour de plusieurs modules:

- `docx_files_merger.py`: Module principal de traitement des documents
- `docx_merger_cli.py`: Interface en ligne de commande améliorée
- `exemple_utilisation.py`: Exemples d'utilisation comme bibliothèque

## Fonctionnalités détaillées

### Extraction de fichiers

L'outil extrait automatiquement tous les fichiers DOC et DOCX d'une archive ZIP, y compris ceux situés dans des sous-dossiers. Les fichiers sont extraits dans un dossier temporaire pour le traitement.

### Conversion DOC vers DOCX

Pour les fichiers au format DOC (ancienne version de Microsoft Word), l'outil tente plusieurs méthodes de conversion:

1. LibreOffice (si installé)
2. Création d'un document de remplacement basique si la conversion n'est pas possible

### Fusion de documents

L'outil fusionne tous les fichiers DOCX en un seul document avec:

- Une page de titre
- Une table des matières
- Des séparateurs entre chaque document
- Des en-têtes indiquant le nom du fichier d'origine

### Conversion en PDF

Le document fusionné est converti en PDF selon plusieurs méthodes possibles:

1. LibreOffice (méthode préférée)
2. Bibliothèque docx2pdf
3. Bibliothèque reportlab pour une version de base

## Utilisation en ligne de commande

### Options avancées

- Génération de rapports: L'option `-r, --rapport` permet de générer un rapport CSV détaillé des résultats
- Mode batch: L'option `-d, --dossier` permet de traiter un dossier entier de fichiers ZIP
- Mode silencieux: L'option `-q, --quiet` désactive l'affichage des barres de progression

### Codes de retour

- `0`: Succès (au moins un fichier traité avec succès)
- `1`: Échec (aucun fichier traité avec succès ou erreur)

## Utilisation comme bibliothèque

### Exemple d'importation

```python
from docx_merger_cli import traiter_fichier, traiter_dossier
```

### Structure des résultats

Les fonctions `traiter_fichier` et `traiter_dossier` retournent des structures de données contenant:

- `statut`: 'succès', 'partiel', ou 'erreur'
- `message`: Description du résultat
- `temps`: Temps de traitement en secondes
- `docx`: Chemin vers le fichier DOCX généré
- `pdf`: Chemin vers le fichier PDF généré

## Dépendances

### Requises
- python-docx
- reportlab

### Optionnelles
- tqdm (pour les barres de progression)
- docx2pdf (pour une meilleure conversion en PDF)
- LibreOffice (pour une conversion optimale)

## Résolution de problèmes

### Conversion DOC vers DOCX échoue
- Vérifiez que LibreOffice est installé
- Pour les fichiers complexes, utilisez une conversion manuelle

### Conversion en PDF échoue
- Assurez-vous que au moins une des méthodes de conversion est disponible
- Vérifiez les permissions des dossiers de sortie

---

Développé par MOA Digital Agency LLC (https://myoneart.com)  
Email: moa@myoneart.com  
Copyright © 2025 MOA Digital Agency LLC.
