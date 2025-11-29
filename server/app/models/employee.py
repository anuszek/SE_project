# Przechowuj info pracownika + ścieżkę do zdjęcia referencyjnego
from datetime import datetime
from app.utils.db import db  

class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    qr_code = db.Column(db.String(255))  # unikalny kod QR
    face_encoding = db.Column(db.LargeBinary)  # zakodowana twarz (numpy array)
    face_image_path = db.Column(db.String(255))  # ścieżka do zdjęcia referencyjnego
    created_at = db.Column(db.DateTime, default=datetime.utcnow)