from app.utils.db import db
from datetime import datetime
import uuid
class QRCredential(db.Model):
    __tablename__ = 'QRCredential'

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    qr_code_data = db.Column(db.String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
 
    expires_at = db.Column(db.DateTime, nullable=True) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_active = db.Column(db.Boolean, default=True)

    # zastąpienie ręcznego setattr by nie łamać domyślnego konstruktora SQLAlchemy
    def __init__(self, **kwargs):
        super().__init__(**kwargs)