# 📑 Documentation Complète DocxFilesMerger

**Version:** 1.0.0  
**Développé par:** MOA Digital Agency LLC (https://myoneart.com)  
**Email:** moa@myoneart.com  
**Copyright:** © 2025 MOA Digital Agency LLC. Tous droits réservés.

## 📋 Table des matières

1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
   - [Installation sur un serveur local](#installation-sur-un-serveur-local)
   - [Installation sur un VPS](#installation-sur-un-vps)
   - [Configuration des variables d'environnement](#configuration-des-variables-denvironnement)
4. [Structure de l'application](#structure-de-lapplication)
5. [Fonctionnalités](#fonctionnalités)
   - [Traitement des fichiers](#traitement-des-fichiers)
   - [Page d'administration](#page-dadministration)
   - [Raccourcis clavier](#raccourcis-clavier)
6. [Base de données](#base-de-données)
   - [Structure des tables](#structure-des-tables)
   - [Migrations](#migrations)
7. [Personnalisation](#personnalisation)
8. [Déploiement](#déploiement)
9. [Dépannage](#dépannage)
10. [Foire aux questions](#foire-aux-questions)

## 📖 Introduction

DocxFilesMerger est une application web développée avec Flask qui permet de traiter et fusionner des documents médicaux (.doc et .docx) stockés dans une archive ZIP. L'application extrait tous les fichiers documents, les convertit en .docx si nécessaire, les fusionne en un seul document et génère également une version PDF du document fusionné.

L'application offre une interface utilisateur intuitive et des fonctionnalités avancées de suivi des statistiques d'utilisation.

## 💻 Prérequis

Avant d'installer DocxFilesMerger, assurez-vous que votre système dispose des éléments suivants :

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- PostgreSQL 12 ou supérieur
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)
- LibreOffice (optionnel, pour une meilleure conversion des documents)

## 🔧 Installation

### Installation sur un serveur local

1. **Cloner le dépôt :**

```bash
git clone https://github.com/moaagency/docxfilesmerger.git
cd docxfilesmerger
```

2. **Créer un environnement virtuel Python :**

```bash
python -m venv venv
```

3. **Activer l'environnement virtuel :**

- Sous Windows :
```bash
venv\Scripts\activate
```

- Sous Linux/Mac :
```bash
source venv/bin/activate
```

4. **Installer les dépendances :**

```bash
pip install docx==0.2.4 docx2pdf==0.1.8 email-validator==2.0.0 flask==2.3.2 flask-sqlalchemy==3.0.5 gunicorn==23.0.0 psycopg2-binary==2.9.6 python-docx==0.8.11 reportlab==4.0.4 werkzeug==2.3.6 python-dotenv==1.0.0
```

5. **Configurer la base de données :**

Créez une base de données PostgreSQL et notez les informations de connexion pour l'étape suivante.

```sql
CREATE DATABASE docxfilesmerger;
CREATE USER docxfilesmerger_user WITH PASSWORD 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE docxfilesmerger TO docxfilesmerger_user;
```

6. **Configuration des variables d'environnement :**

Créez un fichier `.env` à la racine du projet avec les informations suivantes :

```
DATABASE_URL=postgresql://docxfilesmerger_user:mot_de_passe_securise@localhost:5432/docxfilesmerger
FLASK_SECRET_KEY=votre_cle_secrete_tres_securisee
FLASK_APP=main.py
FLASK_ENV=development
```

7. **Lancer l'application :**

```bash
flask run --host=0.0.0.0 --port=5000
```

ou 

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

### Installation sur un VPS

1. **Se connecter au serveur :**

```bash
ssh utilisateur@adresse_ip_serveur
```

2. **Installer les dépendances système :**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx libreoffice-writer
```

3. **Installer les bibliothèques de développement pour PostgreSQL :**

```bash
sudo apt install -y libpq-dev python3-dev
```

4. **Cloner le dépôt :**

```bash
git clone https://github.com/moaagency/docxfilesmerger.git /var/www/docxfilesmerger
cd /var/www/docxfilesmerger
```

5. **Créer et configurer la base de données :**

```bash
sudo -u postgres psql
```

Dans l'interpréteur PostgreSQL :
```sql
CREATE DATABASE docxfilesmerger;
CREATE USER docxfilesmerger_user WITH PASSWORD 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE docxfilesmerger TO docxfilesmerger_user;
\q
```

6. **Configurer l'environnement Python :**

```bash
python3 -m venv venv
source venv/bin/activate
pip install docx==0.2.4 docx2pdf==0.1.8 email-validator==2.0.0 flask==2.3.2 flask-sqlalchemy==3.0.5 gunicorn==23.0.0 psycopg2-binary==2.9.6 python-docx==0.8.11 reportlab==4.0.4 werkzeug==2.3.6 python-dotenv==1.0.0
```

7. **Configurer les variables d'environnement :**

```bash
nano .env
```

Ajoutez les informations suivantes :
```
DATABASE_URL=postgresql://docxfilesmerger_user:mot_de_passe_securise@localhost:5432/docxfilesmerger
FLASK_SECRET_KEY=votre_cle_secrete_tres_securisee
FLASK_APP=main.py
FLASK_ENV=production
```

8. **Configurer un service systemd :**

```bash
sudo nano /etc/systemd/system/docxfilesmerger.service
```

Contenu du fichier :
```
[Unit]
Description=DocxFilesMerger Gunicorn Service
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/docxfilesmerger
Environment="PATH=/var/www/docxfilesmerger/venv/bin"
EnvironmentFile=/var/www/docxfilesmerger/.env
ExecStart=/var/www/docxfilesmerger/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

9. **Configurer Nginx :**

```bash
sudo nano /etc/nginx/sites-available/docxfilesmerger
```

Contenu du fichier :
```
server {
    listen 80;
    server_name votre_domaine.com www.votre_domaine.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/docxfilesmerger/static;
    }

    client_max_body_size 50M;  # Permettre les téléversements de fichiers jusqu'à 50 Mo
}
```

10. **Activer la configuration Nginx :**

```bash
sudo ln -s /etc/nginx/sites-available/docxfilesmerger /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

11. **Démarrer le service :**

```bash
sudo chown -R www-data:www-data /var/www/docxfilesmerger
sudo systemctl enable docxfilesmerger
sudo systemctl start docxfilesmerger
```

### Configuration des variables d'environnement

Voici la description détaillée de chaque variable d'environnement utilisée par l'application :

| Variable | Description | Exemple |
|----------|-------------|---------|
| DATABASE_URL | URL de connexion à la base de données PostgreSQL | postgresql://utilisateur:mot_de_passe@hôte:port/nom_base |
| FLASK_SECRET_KEY | Clé secrète pour la sécurité des sessions | chaîne aléatoire de caractères |
| FLASK_APP | Fichier principal de l'application Flask | main.py |
| FLASK_ENV | Environnement d'exécution (development ou production) | production |

## 📂 Structure de l'application

```
docxfilesmerger/
├── app.py              # Application Flask principale
├── main.py             # Point d'entrée de l'application
├── models.py           # Modèles de base de données
├── utils.py            # Fonctions utilitaires pour le traitement des documents
├── static/             # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   │   └── custom.css  # Styles personnalisés
│   ├── js/
│   │   ├── shortcuts.js # Gestion des raccourcis clavier
│   │   └── upload.js   # Gestion du téléversement de fichiers
│   └── images/         # Images statiques
├── templates/          # Templates Jinja2
│   ├── layout.html     # Template de base
│   ├── index.html      # Page d'accueil
│   ├── admin.html      # Interface d'administration
│   └── error.html      # Pages d'erreur
├── uploads/            # Dossier pour les fichiers téléversés (créé automatiquement)
├── outputs/            # Dossier pour les fichiers traités (créé automatiquement)
└── status/             # Dossier pour les fichiers de statut (créé automatiquement)
```

## 🛠️ Fonctionnalités

### Traitement des fichiers

1. **Téléversement de fichiers ZIP** : L'application accepte les archives ZIP contenant des fichiers .doc et .docx.
2. **Extraction des fichiers** : Les fichiers .doc et .docx sont automatiquement extraits de l'archive.
3. **Conversion des formats** : Les fichiers .doc sont convertis en format .docx.
4. **Fusion des documents** : Tous les fichiers .docx sont fusionnés en un seul document avec une mise en page organisée.
5. **Génération de PDF** : Un fichier PDF est généré à partir du document fusionné.
6. **Téléchargement des résultats** : Les utilisateurs peuvent télécharger le document fusionné au format DOCX ou PDF.

### Page d'administration

La page d'administration offre les fonctionnalités suivantes :

1. **Tableau de bord** : Affiche les statistiques globales d'utilisation (traitements totaux, fichiers traités, temps moyen).
2. **Traitements récents** : Liste des 10 traitements les plus récents avec leur statut et leurs détails.
3. **Statistiques par jour** : Affiche les statistiques d'utilisation quotidiennes.
4. **Configuration** : Permet de modifier les paramètres de l'application.

Pour accéder à la page d'administration, cliquez sur le bouton "Admin" dans le menu principal.

### Raccourcis clavier

L'application prend en charge les raccourcis clavier suivants :

| Raccourci | Action |
|-----------|--------|
| Ctrl+O | Ouvrir la boîte de dialogue de sélection de fichier |
| Esc | Annuler l'opération en cours / Réinitialiser l'application |
| Ctrl+D | Télécharger le document fusionné au format DOCX |
| Ctrl+P | Télécharger le document fusionné au format PDF |
| Ctrl+R | Recharger la page |

## 📊 Base de données

### Structure des tables

L'application utilise trois tables principales dans la base de données :

1. **processing_jobs** : Enregistre les informations sur chaque traitement de fichier.
    - id : Identifiant unique
    - job_id : Identifiant unique du job (chaîne)
    - status : Statut du traitement (uploaded, processing, completed, error)
    - created_at : Date et heure de création
    - completed_at : Date et heure de fin du traitement
    - file_count : Nombre de fichiers traités
    - original_filename : Nom du fichier ZIP original
    - processing_time : Temps de traitement en secondes

2. **usage_stats** : Stocke les statistiques d'utilisation quotidiennes.
    - id : Identifiant unique
    - date : Date des statistiques
    - total_jobs : Nombre total de traitements pour cette date
    - total_files_processed : Nombre total de fichiers traités pour cette date
    - total_processing_time : Temps total de traitement en secondes pour cette date

3. **config** : Stocke les paramètres de configuration de l'application.
    - key : Clé de configuration (identifiant unique)
    - value : Valeur de la configuration
    - description : Description de la configuration
    - updated_at : Date et heure de la dernière mise à jour

### Migrations

L'application crée automatiquement les tables requises lors du premier démarrage. Aucune migration manuelle n'est nécessaire.

Si vous souhaitez réinitialiser la base de données, vous pouvez utiliser les commandes SQL suivantes :

```sql
DROP TABLE IF EXISTS processing_jobs;
DROP TABLE IF EXISTS usage_stats;
DROP TABLE IF EXISTS config;
```

Puis redémarrez l'application pour recréer les tables.

## 🎨 Personnalisation

### Personnalisation de l'interface

Pour personnaliser l'apparence de l'application, vous pouvez modifier les fichiers suivants :

- **static/css/custom.css** : Styles CSS personnalisés
- **templates/layout.html** : Structure générale de l'interface
- **templates/index.html** : Page d'accueil et interface de téléversement

### Personnalisation des fonctionnalités

Pour modifier le comportement de l'application :

- **utils.py** : Contient les fonctions de traitement des documents
- **app.py** : Contient les routes et la logique métier
- **models.py** : Définit les modèles de base de données

## 🚀 Déploiement

### Recommandations pour le déploiement en production

1. **Utiliser un serveur WSGI** : Gunicorn ou uWSGI pour exécuter l'application
2. **Configurer un proxy inverse** : Nginx ou Apache pour gérer les connexions HTTP
3. **Activer HTTPS** : Configurer un certificat SSL avec Let's Encrypt
4. **Sauvegarde de la base de données** : Configurer des sauvegardes régulières
5. **Surveillance** : Mettre en place une surveillance du service et des journaux

### Configuration recommandée pour un trafic moyen

- Serveur : 2 CPU, 4 Go RAM
- Espace disque : 50 Go minimum
- Travailleurs Gunicorn : 3-5
- Nombre maximum de connexions simultanées : 30-50

## 🔍 Dépannage

### Problèmes courants et solutions

1. **Erreur "Le fichier ZIP n'existe pas"**
   - Vérifiez les permissions des dossiers uploads, outputs et status
   - Assurez-vous que le dossier uploads est accessible en écriture

2. **Erreur lors de la conversion en PDF**
   - Vérifiez que LibreOffice est correctement installé
   - Installez les bibliothèques docx2pdf et reportlab

3. **Erreur de connexion à la base de données**
   - Vérifiez les informations de connexion dans le fichier .env
   - Assurez-vous que PostgreSQL est en cours d'exécution

4. **Fichiers non extraits de l'archive ZIP**
   - Vérifiez que l'archive n'est pas corrompue
   - Assurez-vous que l'archive contient des fichiers .doc ou .docx

### Journaux d'erreurs

L'application enregistre les erreurs dans la console et dans les fichiers de statut. Pour les applications déployées avec Gunicorn, consultez les journaux systèmes :

```bash
sudo journalctl -u docxfilesmerger.service
```

## ❓ Foire aux questions

**Q: Quelle est la taille maximale d'un fichier ZIP que je peux téléverser ?**  
R: La taille maximale par défaut est de 50 Mo, mais elle peut être configurée dans le fichier Nginx (client_max_body_size).

**Q: L'application peut-elle traiter d'autres formats de fichiers ?**  
R: Actuellement, seuls les fichiers .doc et .docx sont pris en charge. D'autres formats pourraient être ajoutés dans une version future.

**Q: Est-il possible d'utiliser une autre base de données que PostgreSQL ?**  
R: L'application est conçue pour PostgreSQL, mais peut être adaptée pour d'autres systèmes de gestion de base de données comme MySQL en modifiant la chaîne de connexion et en s'assurant que les types de données sont compatibles.

**Q: Comment ajouter un nouvel utilisateur administrateur ?**  
R: Dans la version actuelle, l'interface d'administration est accessible sans authentification. L'ajout d'un système d'authentification est prévu pour une future version.

**Q: Puis-je utiliser l'application sans connexion Internet ?**  
R: Oui, une fois installée, l'application fonctionne entièrement en local et ne nécessite pas de connexion Internet.

---

## 📧 Support et contact

Pour toute question ou assistance, veuillez contacter :

MOA Digital Agency LLC  
Email : moa@myoneart.com  
Site web : https://myoneart.com

© 2025 MOA Digital Agency LLC. Tous droits réservés.