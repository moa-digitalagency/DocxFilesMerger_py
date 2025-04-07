"""
DocxFilesMerger - Application de traitement et fusion de documents.
Développé par MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialiser SQLAlchemy
db = SQLAlchemy()

class ProcessingJob(db.Model):
    """Modèle pour les traitements de fichiers"""
    __tablename__ = 'processing_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    file_count = db.Column(db.Integer)
    original_filename = db.Column(db.String(255))
    processing_time = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<ProcessingJob {self.job_id}>'
    
    def to_dict(self):
        """Convertir l'objet en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'file_count': self.file_count,
            'original_filename': self.original_filename,
            'processing_time': self.processing_time
        }

class UsageStat(db.Model):
    """Modèle pour les statistiques d'utilisation"""
    __tablename__ = 'usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    total_jobs = db.Column(db.Integer, default=0)
    total_files_processed = db.Column(db.Integer, default=0)
    total_processing_time = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<UsageStat {self.date}>'

class Config(db.Model):
    """Modèle pour les configurations de l'application"""
    __tablename__ = 'config'
    
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.key}>'
    
    @classmethod
    def get_value(cls, key, default=None):
        """Récupérer une valeur de configuration par sa clé"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default
    
    @classmethod
    def set_value(cls, key, value, description=None):
        """Définir une valeur de configuration"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = cls(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()
        return config