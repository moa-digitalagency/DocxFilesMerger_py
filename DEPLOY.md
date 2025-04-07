# Guide de Déploiement de DocxFilesMerger

Ce document détaille les instructions complètes pour déployer l'application DocxFilesMerger sur différents types de serveurs.

## Table des matières

1. [Spécifications minimales requises](#spécifications-minimales-requises)
2. [Déploiement sur un VPS (Serveur dédié/virtuel)](#déploiement-sur-un-vps-serveur-dédiévirtuel)
3. [Déploiement sur un hébergement partagé avec cPanel](#déploiement-sur-un-hébergement-partagé-avec-cpanel)
4. [Configuration de la base de données](#configuration-de-la-base-de-données)
5. [Configuration des variables d'environnement](#configuration-des-variables-denvironnement)
6. [Sécurisation de l'application](#sécurisation-de-lapplication)
7. [Mise à jour de l'application](#mise-à-jour-de-lapplication)
8. [Résolution des problèmes courants](#résolution-des-problèmes-courants)

## Spécifications minimales requises

### Configuration matérielle minimale
- **CPU** : 2 cœurs (4 cœurs recommandés pour les volumes importants)
- **RAM** : 2 Go minimum (4 Go recommandés)
- **Espace disque** : 20 Go minimum (SSD recommandé)
- **Bande passante** : 1 Mbps upload/download minimum

### Logiciels requis
- **Système d'exploitation** : Linux (Ubuntu 20.04 LTS ou plus récent recommandé)
- **Python** : Version 3.7 ou supérieure
- **PostgreSQL** : Version 12 ou supérieure
- **Serveur web** : Nginx ou Apache
- **WSGI** : Gunicorn

### Dépendances Python
```
flask>=2.0.0
flask-sqlalchemy>=3.0.0
gunicorn>=20.0.0
psycopg2-binary>=2.9.0
python-docx>=0.8.10
docx2pdf>=0.1.7
reportlab>=3.6.0
email-validator>=1.1.0
werkzeug>=2.0.0
```

## Déploiement sur un VPS (Serveur dédié/virtuel)

Cette section explique comment déployer l'application sur un serveur VPS Linux.

### Étape 1 : Mise en place du serveur

1. Connectez-vous à votre serveur via SSH :
```bash
ssh utilisateur@adresse-ip-du-serveur
```

2. Mettez à jour le système :
```bash
sudo apt update
sudo apt upgrade -y
```

3. Installez les dépendances système :
```bash
sudo apt install -y python3 python3-pip python3-dev postgresql postgresql-contrib nginx git libpq-dev build-essential libreoffice-writer
```

### Étape 2 : Créer un utilisateur pour l'application

```bash
sudo adduser docxfilesmerger
sudo usermod -aG sudo docxfilesmerger
su - docxfilesmerger
```

### Étape 3 : Cloner le dépôt

```bash
git clone https://github.com/votre-repo/docxfilesmerger.git
cd docxfilesmerger
```

### Étape 4 : Configurer l'environnement Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 5 : Configurer la base de données PostgreSQL

```bash
sudo -u postgres psql
```

Dans l'invite PostgreSQL:
```sql
CREATE DATABASE docxfilesmerger;
CREATE USER docxfilesmerger WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE docxfilesmerger TO docxfilesmerger;
\q
```

### Étape 6 : Configurer les variables d'environnement

Créez un fichier `.env` dans le répertoire du projet :
```bash
nano .env
```

Ajoutez les variables suivantes :
```
FLASK_APP=app.py
FLASK_ENV=production
DATABASE_URL=postgresql://docxfilesmerger:votre_mot_de_passe_securise@localhost/docxfilesmerger
FLASK_SECRET_KEY=votre_cle_secrete_ultra_securisee
```

### Étape 7 : Configurer Gunicorn

Créez un fichier service systemd pour exécuter Gunicorn en permanence :

```bash
sudo nano /etc/systemd/system/docxfilesmerger.service
```

Ajoutez le contenu suivant :
```
[Unit]
Description=DocxFilesMerger Gunicorn Service
After=network.target

[Service]
User=docxfilesmerger
Group=www-data
WorkingDirectory=/home/docxfilesmerger/docxfilesmerger
Environment="PATH=/home/docxfilesmerger/docxfilesmerger/venv/bin"
EnvironmentFile=/home/docxfilesmerger/docxfilesmerger/.env
ExecStart=/home/docxfilesmerger/docxfilesmerger/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activez et démarrez le service :
```bash
sudo systemctl enable docxfilesmerger
sudo systemctl start docxfilesmerger
```

### Étape 8 : Configurer Nginx comme proxy inverse

Créez un fichier de configuration Nginx :
```bash
sudo nano /etc/nginx/sites-available/docxfilesmerger
```

Ajoutez le contenu suivant :
```
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    client_max_body_size 500M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        include proxy_params;
        proxy_pass http://localhost:5000;
    }
}
```

Activez le site et redémarrez Nginx :
```bash
sudo ln -s /etc/nginx/sites-available/docxfilesmerger /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Étape 9 : Configurer HTTPS avec Let's Encrypt (recommandé)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

## Déploiement sur un hébergement partagé avec cPanel

### Étape 1 : Préparer les fichiers

1. Sur votre machine locale, créez un fichier `requirements.txt` contenant toutes les dépendances Python.
2. Compressez votre projet au format ZIP.

### Étape 2 : Accéder à cPanel

1. Connectez-vous à votre panneau cPanel via l'URL fournie par votre hébergeur.
2. Cherchez la section "Applications Python" ou "Configurateur Python".

### Étape 3 : Créer une application Python

1. Créez une nouvelle application Python.
2. Sélectionnez Python 3.7 ou une version plus récente.
3. Définissez le chemin de l'application (généralement `public_html/docxfilesmerger` ou un sous-domaine).
4. Définissez le point d'entrée de l'application comme `main.py`.
5. Activez l'environnement virtuel.

### Étape 4 : Télécharger les fichiers

1. Utilisez le Gestionnaire de fichiers cPanel pour naviguer vers le répertoire de votre application.
2. Téléchargez le fichier ZIP de votre projet.
3. Extrayez le fichier ZIP dans le répertoire.

### Étape 5 : Installer les dépendances

Dans le terminal SSH de cPanel (si disponible) ou via l'interface Python :
```bash
cd public_html/docxfilesmerger
pip install -r requirements.txt
```

### Étape 6 : Configurer la base de données

1. Dans cPanel, accédez à "Bases de données MySQL" ou "PostgreSQL" (selon la disponibilité).
2. Créez une nouvelle base de données et un utilisateur.
3. Créez un fichier `.env` dans le répertoire de votre application avec les détails de connexion.

### Étape 7 : Configurer le serveur web

En fonction de l'hébergement partagé, vous devrez peut-être créer un fichier `.htaccess` pour Apache :
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

### Étape 8 : Adapter l'application pour l'hébergement partagé

1. Modifiez `main.py` pour prendre en charge le mode WSGI :
```python
# En haut du fichier
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# À la fin du fichier
application = app  # pour WSGI
```

2. Vérifiez que les chemins absolus sont adaptés à l'environnement d'hébergement partagé.

## Configuration de la base de données

### Structure SQL

Voici le schéma SQL pour la base de données de l'application :

```sql
-- Table pour stocker les informations des traitements
CREATE TABLE processing_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    file_count INTEGER,
    original_filename VARCHAR(255),
    processing_time INTEGER
);

-- Table pour les statistiques d'utilisation
CREATE TABLE usage_stats (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    total_jobs INTEGER DEFAULT 0,
    total_files_processed INTEGER DEFAULT 0,
    total_processing_time INTEGER DEFAULT 0
);

-- Table pour les paramètres de configuration
CREATE TABLE config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insérer les configurations par défaut
INSERT INTO config (key, value, description) VALUES
('max_upload_size', '500', 'Taille maximale d''upload en Mo'),
('max_file_age_hours', '24', 'Durée de conservation des fichiers temporaires en heures'),
('enable_pdf_conversion', 'true', 'Activer la conversion PDF');
```

### Migration initiale

Pour initialiser la base de données :

```bash
psql -U docxfilesmerger -d docxfilesmerger -a -f schema.sql
```

## Configuration des variables d'environnement

Les variables d'environnement suivantes doivent être définies :

| Variable | Description | Exemple |
|----------|-------------|---------|
| DATABASE_URL | URL de connexion à la base de données | postgresql://user:password@localhost/docxfilesmerger |
| FLASK_SECRET_KEY | Clé secrète pour Flask | une_chaine_aleatoire_tres_longue |
| FLASK_ENV | Environnement d'exécution (development/production) | production |
| UPLOAD_MAX_SIZE | Taille maximale d'upload en Mo | 500 |
| LOG_LEVEL | Niveau de journalisation | INFO |

## Sécurisation de l'application

### Recommandations de sécurité

1. **Toujours utiliser HTTPS** avec un certificat SSL valide.
2. **Limiter les autorisations de fichiers** :
   ```bash
   chmod -R 750 /home/docxfilesmerger/docxfilesmerger
   chmod 640 /home/docxfilesmerger/docxfilesmerger/.env
   ```
3. **Configurer un pare-feu** :
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```
4. **Mettre à jour régulièrement** les dépendances et le système.
5. **Sauvegarder régulièrement** la base de données et les configurations.

## Mise à jour de l'application

Pour mettre à jour l'application :

```bash
cd /home/docxfilesmerger/docxfilesmerger
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart docxfilesmerger
```

## Résolution des problèmes courants

### L'application ne démarre pas

Vérifiez les journaux :
```bash
sudo journalctl -u docxfilesmerger.service -n 50
```

### Erreurs de permissions

Vérifiez que les dossiers d'upload et de sortie ont les bonnes permissions :
```bash
sudo chown -R docxfilesmerger:www-data /home/docxfilesmerger/docxfilesmerger/uploads
sudo chown -R docxfilesmerger:www-data /home/docxfilesmerger/docxfilesmerger/outputs
```

### Problèmes de conversion PDF

1. Vérifiez que LibreOffice est installé :
```bash
libreoffice --version
```

2. Testez la conversion manuellement :
```bash
libreoffice --headless --convert-to pdf document.docx
```

### Timeouts sur les uploads volumineux

Ajustez les paramètres de timeout dans Nginx et Gunicorn.

Nginx:
```
client_max_body_size 1000M;
proxy_read_timeout 600;
proxy_connect_timeout 600;
proxy_send_timeout 600;
```

Gunicorn (dans docxfilesmerger.service) :
```
ExecStart=/home/docxfilesmerger/docxfilesmerger/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 600 main:app
```

---

Pour toute assistance supplémentaire, contactez le support technique à l'adresse [moa@myoneart.com](mailto:moa@myoneart.com).