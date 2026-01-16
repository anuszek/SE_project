from datetime import datetime, timezone
from app.utils.db import db

class FaceCredential(db.Model):
    __tablename__ = 'face_credential'

    id = db.Column(db.Integer, primary_key=True)
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)
    
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    face_image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))