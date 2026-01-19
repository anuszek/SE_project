from datetime import datetime, timezone
from app.utils.db import db  

class FaceCredential(db.Model):
    __tablename__ = 'face_credential'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)
    
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    face_image = db.Column(db.LargeBinary) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    face_encoding_addidional_1 = db.Column(db.LargeBinary, nullable=True)
    face_image_addidional_1 = db.Column(db.LargeBinary, nullable=True)
    created_at_addidional_1 = db.Column(db.DateTime, nullable=True)

    face_encoding_addidional_2 = db.Column(db.LargeBinary, nullable=True)
    face_image_addidional_2 = db.Column(db.LargeBinary, nullable=True)
    created_at_addidional_2 = db.Column(db.DateTime, nullable=True)

    def register_dynamic_entry(self, new_encoding_bytes, new_image_bytes):
        """
        Logic to register a new additional face encoding.
        Fills the first available slot, or overwrites the oldest if both are occupied.
        Returns a message indicating the action taken.
        1. If Slot 1 is empty, fill it.
        2. Else if Slot 2 is empty, fill it.
        3. Else, compare timestamps and overwrite the oldest slot.
        """
        now = datetime.now(timezone.utc)

        if self.face_encoding_addidional_1 is None:
            self.face_encoding_addidional_1 = new_encoding_bytes
            self.face_image_addidional_1 = new_image_bytes
            self.created_at_addidional_1 = now
            return "Saved in Slot 1 (was empty)"

        if self.face_encoding_addidional_2 is None:
            self.face_encoding_addidional_2 = new_encoding_bytes
            self.face_image_addidional_2 = new_image_bytes
            self.created_at_addidional_2 = now
            return "Saved in Slot 2 (was empty)"
        
        date1 = self.created_at_addidional_1 or datetime.min.replace(tzinfo=timezone.utc)
        date2 = self.created_at_addidional_2 or datetime.min.replace(tzinfo=timezone.utc)

        if date1 < date2:
            self.face_encoding_addidional_1 = new_encoding_bytes
            self.face_image_addidional_1 = new_image_bytes
            self.created_at_addidional_1 = now
            return "Overwritten Slot 1 (was oldest)"
        else:
            self.face_encoding_addidional_2 = new_encoding_bytes
            self.face_image_addidional_2 = new_image_bytes
            self.created_at_addidional_2 = now
            return "Overwritten Slot 2 (was oldest)"