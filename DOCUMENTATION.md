# Documentation de DocxFilesMerger CLI

## Vue d'ensemble

DocxFilesMerger CLI est un outil en ligne de commande conçu pour traiter des archives ZIP contenant des documents médicaux. Il permet d'extraire, convertir et fusionner des fichiers DOC et DOCX, puis de générer un PDF du document fusionné, le tout sans nécessiter d'interface graphique.

## Architecture

L'application est structurée autour de plusieurs modules:

- `main.py`: Point d'entrée principal et interface CLI simplifiée
- `docx_files_merger.py`: Module principal de traitement des documents
- `docx_merger_cli.py`: Fonctionnalités avancées de ligne de commande
- `demo_cli.py`: Mode démonstration automatique
- `exemple_utilisation.py`: Exemples d'utilisation comme bibliothèque
- `utils.py`: Fonctions utilitaires communes

## Installation et prérequis

### Prérequis système
- Python 3.8 ou supérieur
- Bibliothèques Python requises (voir ci-dessous)
- Espace disque pour les fichiers temporaires et de sortie

### Installation des dépendances

```bash
pip install docx python-docx reportlab docx2pdf email-validator
```

### Installation de LibreOffice (optionnel mais recommandé)

Pour une meilleure conversion des documents, l'installation de LibreOffice est recommandée:

- **Debian/Ubuntu**: `sudo apt-get install libreoffice`
- **Fedora/RHEL**: `sudo dnf install libreoffice`
- **Windows**: Téléchargez et installez à partir de libreoffice.org
- **macOS**: Installez via Homebrew: `brew install --cask libreoffice`

## Fonctionnalités détaillées

### Mode démonstration automatique

Le mode démo (sans arguments) crée automatiquement:
1. Des fichiers DOCX de test avec du contenu différent
2. Une archive ZIP contenant ces fichiers
3. Exécute le traitement complet pour montrer les capacités de l'outil

### Extraction de fichiers

L'outil extrait automatiquement tous les fichiers DOC et DOCX d'une archive ZIP, y compris ceux situés dans des sous-dossiers. Le processus gère:
- La détection des extensions .doc et .docx
- La gestion des noms de fichiers avec caractères spéciaux
- La préservation de la structure des noms pour le document final

### Conversion DOC vers DOCX

Pour les fichiers au format DOC (ancienne version de Microsoft Word), l'outil utilise plusieurs méthodes de conversion par ordre de priorité:

1. LibreOffice (via l'interface de ligne de commande)
2. Création d'un document DOCX de remplacement si la conversion n'est pas possible

### Fusion de documents

L'outil fusionne tous les fichiers DOCX en un seul document avec:

- Des sauts de section entre les documents
- Des en-têtes indiquant le nom du fichier d'origine
- Une préservation des styles et de la mise en forme
- La gestion des conflits de styles

### Conversion en PDF

Le document fusionné est converti en PDF selon plusieurs méthodes, avec une cascade de repli:

1. LibreOffice (méthode préférée pour la fidélité)
2. Bibliothèque docx2pdf (alternative)
3. Bibliothèque reportlab (solution de repli basique)

## Utilisation en ligne de commande

### Syntaxe de base

```bash
python main.py [options]
```

### Options disponibles

| Option | Description |
|--------|-------------|
| `-f, --fichier FICHIER` | Chemin vers un fichier ZIP à traiter |
| `-d, --dossier DOSSIER` | Chemin vers un dossier contenant des fichiers ZIP |
| `-o, --output DOSSIER` | Dossier de sortie pour les résultats (défaut: ./output) |
| `-q, --quiet` | Mode silencieux (sans affichage de progression) |
| `-r, --rapport FICHIER` | Générer un rapport CSV des résultats |
| `-h, --help` | Afficher l'aide |

### Exemples d'utilisation

#### Mode démonstration (sans arguments)
```bash
python main.py
```

#### Traiter un fichier spécifique
```bash
python main.py -f dossier/archive.zip -o ./resultats
```

#### Traiter un dossier et générer un rapport
```bash
python main.py -d ./dossier_archives -o ./resultats -r rapport.csv
```

#### Utiliser le script shell (Unix/Linux/macOS)
```bash
./start_cli.sh -f archive.zip
```

### Codes de retour

- `0`: Succès (au moins un fichier traité avec succès)
- `1`: Échec (aucun fichier traité avec succès ou erreur)

## Utilisation comme bibliothèque

### Intégration dans vos scripts

```python
# Importer les fonctions principales
from docx_merger_cli import traiter_fichier, traiter_dossier, generer_rapport

# Traiter un fichier ZIP unique
resultat = traiter_fichier("chemin/vers/archive.zip", "./resultats")

# Traiter tous les fichiers ZIP d'un dossier
resultats = traiter_dossier("chemin/vers/dossier", "./resultats")

# Générer un rapport CSV
generer_rapport(resultats, "rapport.csv")

# Vérifier les résultats
if resultat["statut"] == "succès":
    print(f"Traitement réussi en {resultat['temps']:.2f} secondes")
    print(f"Document DOCX: {resultat['docx']}")
    print(f"Document PDF: {resultat['pdf']}")
```

### Structure des résultats

Les fonctions retournent des dictionnaires (ou listes de dictionnaires) contenant:

| Clé | Description |
|-----|-------------|
| `statut` | État du traitement: 'succès', 'partiel', ou 'erreur' |
| `message` | Description détaillée du résultat |
| `temps` | Temps de traitement en secondes |
| `docx` | Chemin complet vers le fichier DOCX généré |
| `pdf` | Chemin complet vers le fichier PDF généré |
| `fichier` | (Uniquement pour traiter_dossier) Fichier source traité |

## Détails techniques

### Structure des dossiers de sortie

Pour un traitement de fichier unique avec `-f archive.zip -o ./resultats`:
```
resultats/
  ├── extracted/            # Fichiers extraits de l'archive
  │   ├── document1.docx
  │   ├── document2.docx
  │   └── ...
  ├── merged.docx           # Document DOCX fusionné
  └── merged.pdf            # Document PDF généré
```

Pour un traitement par lot avec `-d ./archives -o ./resultats`:
```
resultats/
  ├── archive1/             # Résultats pour la première archive
  │   ├── extracted/
  │   ├── merged.docx
  │   └── merged.pdf
  ├── archive2/             # Résultats pour la deuxième archive
  │   ├── extracted/
  │   ├── merged.docx
  │   └── merged.pdf
  └── ...
```

### Format du rapport CSV

Le rapport CSV généré contient les colonnes suivantes:
- Date: Date et heure du traitement
- Fichier: Nom du fichier ZIP traité
- Statut: Résultat du traitement
- Temps (s): Durée en secondes
- DOCX: Nom du fichier DOCX généré
- PDF: Nom du fichier PDF généré
- Message: Détails sur le traitement

## Résolution de problèmes

### Conversion DOC vers DOCX échoue
- Vérifiez que LibreOffice est correctement installé et accessible
- Pour les fichiers complexes, convertissez-les manuellement avant le traitement

### Conversion en PDF échoue
- Vérifiez la présence d'au moins une des méthodes de conversion (LibreOffice, docx2pdf)
- Assurez-vous que les permissions des dossiers permettent l'écriture
- En cas d'erreur avec docx2pdf, essayez d'installer Microsoft Word (Windows uniquement)

### Problèmes de mémoire
- Pour les très grands ensembles de documents, augmentez la mémoire disponible
- Traitez les fichiers par petits lots plutôt qu'en une seule opération

---

Développé par MOA Digital Agency LLC (https://myoneart.com)  
Email: moa@myoneart.com  
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
