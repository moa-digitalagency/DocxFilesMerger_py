# DocxFilesMerger CLI

Un outil en ligne de commande amélioré pour traiter des documents médicaux à partir d'archives ZIP.

## Fonctionnalités

- Extraction automatique des fichiers DOC/DOCX d'une archive ZIP
- Conversion des fichiers DOC au format DOCX
- Fusion de tous les documents en un seul fichier DOCX unifié
- Génération automatique d'une version PDF du document fusionné
- Barre de progression pour suivre l'avancement du traitement
- Traitement de fichiers individuels ou de dossiers entiers
- Génération de rapports CSV des résultats
- Interface en ligne de commande flexible et puissante

## Installation

1. Assurez-vous d'avoir Python 3.8 ou supérieur installé
2. Installez les dépendances requises
3. Pour une meilleure expérience, installez les dépendances optionnelles
4. Pour une conversion optimale, installez LibreOffice

## Utilisation

### Traiter un seul fichier ZIP

```bash
python docx_merger_cli.py -f chemin/vers/archive.zip -o ./resultats
```

### Traiter tous les fichiers ZIP d'un dossier

```bash
python docx_merger_cli.py -d chemin/vers/dossier -o ./resultats
```

### Options disponibles

- `-f, --fichier FICHIER` : Traiter un seul fichier ZIP
- `-d, --dossier DOSSIER` : Traiter tous les fichiers ZIP d'un dossier
- `-o, --output DOSSIER` : Dossier de sortie pour les résultats
- `-q, --quiet` : Mode silencieux, sans affichage des barres de progression
- `-r, --rapport FICHIER` : Générer un rapport CSV des résultats de traitement
- `-h, --help` : Afficher l'aide complète

## Exemples d'utilisation

### Traiter un fichier et générer un rapport

```bash
python docx_merger_cli.py -f archive.zip -o ./resultats -r rapport.csv
```

### Traiter tous les fichiers d'un dossier en mode silencieux

```bash
python docx_merger_cli.py -d ./dossier_archives -o ./resultats -q
```

## Utilisation comme bibliothèque Python

Vous pouvez également utiliser DocxFilesMerger comme une bibliothèque dans vos propres scripts.
Voir `exemple_utilisation.py` pour un exemple complet.

---

Développé par MOA Digital Agency LLC (https://myoneart.com)  
Email: moa@myoneart.com  
Copyright © 2025 MOA Digital Agency LLC.
