# 📋 DocxFilesMerger 🏥

## 🌟 Présentation

Bienvenue dans l'application **DocxFilesMerger** ! 🎉
Cette application web permet de traiter efficacement et rapidement des archives ZIP contenant des milliers de dossiers médicaux au format .doc ou .docx.

![Badge Langage](https://img.shields.io/badge/Langage-Python-blue)
![Badge Framework](https://img.shields.io/badge/Framework-Flask-green)
![Badge Version](https://img.shields.io/badge/Version-1.0.0-orange)

### 📝 Développeur

**MOA Digital Agency LLC**  
Site web: [https://myoneart.com](https://myoneart.com)  
Contact: [moa@myoneart.com](mailto:moa@myoneart.com)

## 🚀 Fonctionnalités principales

- ✅ **Extraction de fichiers** : Extrait automatiquement tous les fichiers .doc et .docx d'une archive ZIP
- ✅ **Conversion de format** : Convertit les fichiers .doc en .docx si nécessaire
- ✅ **Fusion de documents** : Combine tous les fichiers en un seul document avec des séparateurs clairs
- ✅ **Conversion PDF** : Génère une version PDF du document fusionné
- ✅ **Interface utilisateur intuitive** : Interface web simple et réactive pour téléverser et télécharger des fichiers

## 🔍 Comment ça fonctionne

1. 📤 **Téléversez** une archive ZIP contenant des dossiers médicaux (.doc/.docx)
2. ⚙️ Le système **extrait** tous les fichiers pertinents
3. 🔄 Les fichiers sont **convertis** (si nécessaire) et **fusionnés** en un seul document
4. 📑 Une **séparation claire** est ajoutée avant chaque dossier : `<NOMFICHIER.extension>...`
5. 📊 Le système génère automatiquement des **versions DOCX et PDF** du document final
6. 📥 **Téléchargez** les documents finaux une fois le traitement terminé

## 💻 Technologies utilisées

- **Backend** : Python, Flask
- **Traitement de documents** : python-docx, docx2pdf
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap
- **Système de fichiers** : Gestion temporaire des fichiers zipfile
- **Base de données** : PostgreSQL (pour le suivi des traitements)

## 🚀 Déploiement

L'application peut être déployée sur différents types de serveurs :

### Configuration système minimale
- **CPU** : 2 cœurs (4 recommandés)  
- **RAM** : 2 Go minimum (4 Go recommandés)
- **Espace disque** : 20 Go minimum
- **OS** : Linux (Ubuntu 20.04 LTS ou plus récent recommandé)

### Guide rapide de déploiement

1. **Serveur VPS / Dédié** :
   ```bash
   # Installation des dépendances
   sudo apt update && sudo apt install -y python3 python3-pip python3-venv postgresql nginx libreoffice-writer
   
   # Clonage du dépôt
   git clone https://github.com/votre-repo/docxfilesmerger.git
   cd docxfilesmerger
   
   # Configuration de l'environnement
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configuration de la base de données PostgreSQL
   sudo -u postgres createdb docxfilesmerger
   sudo -u postgres psql -c "CREATE USER docxfilesmerger WITH PASSWORD 'password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE docxfilesmerger TO docxfilesmerger;"
   
   # Démarrage avec Gunicorn
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

2. **Hébergement partagé avec cPanel** :
   - Assurez-vous que votre hébergement supporte Python 3.7+ et PostgreSQL
   - Créez une application Python via l'interface cPanel
   - Téléchargez les fichiers de l'application
   - Créez une base de données PostgreSQL via cPanel
   - Configurez le fichier `.htaccess` pour Apache
   ```
   RewriteEngine On
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteRule ^(.*)$ /main.py [QSA,L]
   
   <Files ~ "\.(py|env)$">
       Order allow,deny
       Deny from all
   </Files>
   
   <Files main.py>
       SetHandler wsgi-script
       Options +ExecCGI
   </Files>
   ```

### Documentation détaillée

Pour des instructions complètes sur le déploiement, voir notre documentation détaillée disponible à [moa@myoneart.com](mailto:moa@myoneart.com).

## 🛠️ Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| <kbd>Ctrl</kbd> + <kbd>O</kbd> | Ouvrir le sélecteur de fichiers |
| <kbd>Esc</kbd> | Annuler l'opération en cours |
| <kbd>Ctrl</kbd> + <kbd>D</kbd> | Télécharger le document DOCX |
| <kbd>Ctrl</kbd> + <kbd>P</kbd> | Télécharger le document PDF |
| <kbd>Ctrl</kbd> + <kbd>R</kbd> | Réinitialiser l'application |

## 📋 Prérequis

- Python 3.7+
- Bibliothèques Python : flask, python-docx, docx2pdf, etc.
- Navigateur web moderne (Chrome, Firefox, Safari, Edge)

## ⚠️ Remarques importantes

- 🔒 **Confidentialité** : Cette application traite les fichiers localement et ne les envoie pas sur des serveurs externes
- 📦 **Taille maximale** : L'application a été testée avec des archives contenant plus de 5 000 fichiers
- ⏱️ **Temps de traitement** : Le traitement peut prendre plusieurs minutes pour les grandes archives
- 🧹 **Nettoyage automatique** : Les fichiers temporaires sont automatiquement supprimés après 24 heures

## 🔧 Dépannage

| Problème | Solution |
|----------|----------|
| L'archive ZIP n'est pas acceptée | Vérifiez que le fichier est bien au format ZIP (et non RAR ou 7z) |
| Erreur lors de l'extraction | Assurez-vous que l'archive n'est pas corrompue |
| Conversion PDF échoue | Installez LibreOffice pour améliorer la conversion PDF |
| Fichiers manquants | Seuls les fichiers .doc et .docx sont traités, les autres formats sont ignorés |

## 📞 Support

Pour toute question ou problème, n'hésitez pas à :
- 📧 Contacter le support : [moa@myoneart.com](mailto:moa@myoneart.com)
- 🌐 Visiter notre site web : [https://myoneart.com](https://myoneart.com)

## 📜 Licence

Ce projet est développé par MOA Digital Agency LLC. Tous droits réservés © 2025.
