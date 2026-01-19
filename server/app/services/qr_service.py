import base64
import io
import uuid
from datetime import datetime, timedelta
from app.models.qr_code import QRCredential
from app.utils.db import db

class QRService:

    @staticmethod
    def generate_credential(valid_minutes: int = 3600):
        """
        Generates a unique QR code data and its expiration date.
        """

        qr_code_data = str(uuid.uuid4())

        expiration = datetime.utcnow() + timedelta(minutes=valid_minutes)
        return qr_code_data, expiration
    
    @staticmethod
    def validate_qr_code(qr_code_data: str):
        """
        Validates the provided QR code data.
        """

        if not qr_code_data:
            return False

        credential = QRCredential.query.filter_by(qr_code_data=qr_code_data).first()
        if not credential:
            return False
        if not credential.is_active:
            return False
    
        if credential.expires_at and credential.expires_at < datetime.utcnow():
            credential.is_active = False
            db.session.add(credential)
            db.session.commit()
            return False

        return True