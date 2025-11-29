from datetime import datetime
from app.utils.db import db

class FaceCredential(db.Model):
    # Nazwa tabeli w bazie (małymi literami to konwencja)
    __tablename__ = 'face_credential'

    # Musi być Primary Key!
    id = db.Column(db.Integer, primary_key=True)
    
    # Klucz obcy do pracownika
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)
    
    # Dane biometryczne
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    face_image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)