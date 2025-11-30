import base64
import io
import uuid
from datetime import datetime, timedelta
from app.models.qr_code import QRCredential
import segno

class QRService:

    @staticmethod
    def generate_credential(valid_weeks: int = 4):

        qr_code_data = str(uuid.uuid4())

        expiration = datetime.utcnow() + timedelta(weeks=valid_weeks)
        return qr_code_data, expiration
    
    @staticmethod
    def generate_qr_img(qr_code_data: str):

        qr = segno.make(qr_code_data)

        img_buffer = io.BytesIO()
        qr.save(img_buffer, kind='png', scale=5, dark='black', light='white')
        img_buffer.seek(0)

        return img_buffer.read()
    
    @staticmethod
    def generate_qr_data_uri(qr_code_data: str):
        """
        Wygodny wrapper: zwraca data:image/png;base64,...
        """
        png = QRService.generate_qr_img(qr_code_data)
        return "data:image/png;base64," + base64.b64encode(png).decode("ascii")
    
    @staticmethod
    def validate_qr_code(qr_code_data: str):

        credential = QRCredential.query.filter_by(qr_code_data=qr_code_data).first()
        if not credential:
            return False, "Invalid QR code."
        if not credential.is_active:
            return False, "QR code is inactive."
        if credential.expires_at and credential.expires_at < datetime.now():
            return False, "QR code has expired."
        if credential.qr_code_data != qr_code_data:
            return False, "QR code data does not match."

        return True, "QR code is valid."