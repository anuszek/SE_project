# Przechowuj info pracownika + ścieżkę do zdjęcia referencyjnego
from datetime import datetime
from app.utils.db import db  

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    face_data = db.relationship('FaceCredential', backref='employee', uselist=False, cascade="all, delete-orphan")
    qr_code   = db.relationship('QRCredential', backref='employee', uselist=False, cascade="all, delete-orphan")