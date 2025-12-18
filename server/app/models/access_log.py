from datetime import datetime
from app.utils.db import db

class AccessLog(db.Model):
    __tablename__ = 'access_log'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'granted' lub 'denied'
    verification_method = db.Column(db.String(50), nullable=False)  # 'face' lub 'qr'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacja z Employee
    employee = db.relationship('Employee', backref='access_logs')
    
    def __repr__(self):
        return f'<AccessLog {self.id}: {self.employee_id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}",
            'status': self.status,
            'verification_method': self.verification_method,
            'timestamp': self.timestamp.isoformat()
        }