from datetime import datetime, timezone
from app.utils.db import db  # Zakładam, że tu masz instancję SQLAlchemy

class FaceCredential(db.Model):
    __tablename__ = 'face_credential'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)
    
    # --- DANE GŁÓWNE (STAŁE) ---
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    face_image = db.Column(db.LargeBinary) # Zmiana na LargeBinary (BLOB)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # --- SLOT 1 (ZMIENNE) ---
    # Ważne: nullable=True, aby slot mógł być pusty na początku
    face_encoding_addidional_1 = db.Column(db.LargeBinary, nullable=True)
    face_image_addidional_1 = db.Column(db.LargeBinary, nullable=True)
    created_at_addidional_1 = db.Column(db.DateTime, nullable=True)

    # --- SLOT 2 (ZMIENNE) ---
    face_encoding_addidional_2 = db.Column(db.LargeBinary, nullable=True)
    face_image_addidional_2 = db.Column(db.LargeBinary, nullable=True)
    created_at_addidional_2 = db.Column(db.DateTime, nullable=True)

    def register_dynamic_entry(self, new_encoding_bytes, new_image_bytes):
        """
        Logika aktualizacji twarzy:
        1. Jeśli Slot 1 pusty -> zapisz w Slot 1.
        2. Jeśli Slot 2 pusty -> zapisz w Slot 2.
        3. Jeśli oba pełne -> nadpisz ten z najstarszą datą.
        """
        now = datetime.now(timezone.utc)

        # 1. Sprawdź czy Slot 1 jest wolny
        if self.face_encoding_addidional_1 is None:
            self.face_encoding_addidional_1 = new_encoding_bytes
            self.face_image_addidional_1 = new_image_bytes
            self.created_at_addidional_1 = now
            return "Zapisano w Slot 1 (był pusty)"

        # 2. Sprawdź czy Slot 2 jest wolny
        if self.face_encoding_addidional_2 is None:
            self.face_encoding_addidional_2 = new_encoding_bytes
            self.face_image_addidional_2 = new_image_bytes
            self.created_at_addidional_2 = now
            return "Zapisano w Slot 2 (był pusty)"

        # 3. Oba zajęte - porównaj daty i nadpisz starszy
        # Używamy datetime.min jako zabezpieczenia, gdyby data była None (choć nie powinna)
        date1 = self.created_at_addidional_1 or datetime.min.replace(tzinfo=timezone.utc)
        date2 = self.created_at_addidional_2 or datetime.min.replace(tzinfo=timezone.utc)

        if date1 < date2:
            # Slot 1 jest starszy
            self.face_encoding_addidional_1 = new_encoding_bytes
            self.face_image_addidional_1 = new_image_bytes
            self.created_at_addidional_1 = now
            return "Nadpisano Slot 1 (był najstarszy)"
        else:
            # Slot 2 jest starszy (lub taki sam)
            self.face_encoding_addidional_2 = new_encoding_bytes
            self.face_image_addidional_2 = new_image_bytes
            self.created_at_addidional_2 = now
            return "Nadpisano Slot 2 (był najstarszy)"