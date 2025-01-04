from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

# Tabla: user
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    streak = db.Column(db.Integer, default=0)  # Se asume que el streak inicia en 0
    last_streak_update = db.Column(db.DateTime, default=datetime.utcnow)
    quetzalito = db.Column(db.String(120), nullable=True)  # Se asume que puede ser nulo
    confirmed = db.Column(db.Boolean, default=False)
    videos = relationship('Video', backref='user', cascade="all, delete", lazy=True)
    traducciones = relationship('Traduccion', backref='user', cascade="all, delete", lazy=True)
    dictionary_entries = relationship('Dictionary', backref='user', cascade="all, delete", lazy=True)

    def __repr__(self):
        return f'<User {self.mail}>'

# Tabla: video
class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    traduction_esp = db.Column(db.String(255), nullable=True)
    sentence_lensegua = db.Column(db.String(255), nullable=False)
    video = db.Column(db.String(255), nullable=False)  # Ruta del video
    prev_image = db.Column(db.String(255), nullable=True)  # Ruta de la imagen previa
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Video {self.id} para usuario {self.id_user}>'

# Tabla: traduccion
class Traduccion(db.Model):
    __tablename__ = 'traduccion'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sentence_lensegua = db.Column(db.String(255), nullable=False)
    traduction_esp = db.Column(db.String(255), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Traduccion {self.id} para usuario {self.id_user}>'

# Tabla: dictionary
class Dictionary(db.Model):
    __tablename__ = 'dictionary'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_word = db.Column(db.String(255), nullable=False)  # Este ID no es único
    
    def __repr__(self):
        return f'<Dictionary {self.id_word} para usuario {self.id_user}>'