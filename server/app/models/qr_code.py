from app.utils.db import db
from datetime import datetime
class QRCredential(db.Model):
    __tablename__ = 'QRCredential'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)
    
    qr_code_data = db.Column(db.String(255), unique=True, nullable=False) # Unikalny ciąg znaków QR
 
    expires_at = db.Column(db.DateTime, nullable=True) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)