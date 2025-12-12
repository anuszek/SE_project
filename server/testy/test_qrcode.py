import base64
from datetime import datetime, timedelta
from unittest.mock import patch
import numpy as np

from app.models.qr_code import QRCredential
from app.models.employee import Employee
from app.utils.db import db
from app.utils.helpers import refresh_expired_qr_codes, delete_inactive_qr_codes
from app.services.qr_service import QRService


def _fake_b64_image():
    return "data:image/jpeg;base64," + base64.b64encode(b"fake-image").decode("ascii")


def test_register_creates_qr_code(client):
    """
    Test: rejestracja -> zwraca qr_code -> GET /qr zwraca qr_code.
    """
    img_b64 = _fake_b64_image()
    fake_encoding = np.zeros(128, dtype=np.float64)
    fake_bytes = b"fake-encoding-bytes"

    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as mock_enc_to_bytes:

        mock_get_enc.return_value = fake_encoding
        mock_enc_to_bytes.return_value = fake_bytes

        payload = {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "email": "jan.kowalski@example.com",
            "image": img_b64
        }

        resp = client.post("/api/employees/register", json=payload)
        assert resp.status_code == 201, resp.get_json()
        data = resp.get_json()
        assert "employee_id" in data
        assert "qr_code" in data
        emp_id = data["employee_id"]
        qr_code = data["qr_code"]

        # GET /qr endpoint powinien zwrócić qr_code
        get_resp = client.get(f"/api/employees/{emp_id}/qr")
        assert get_resp.status_code == 200, get_resp.get_json()
        j = get_resp.get_json()
        assert "qr_code" in j
        assert j["qr_code"] == qr_code
        assert "expires_at" in j


def test_validate_qr_code(app, client):
    """
    Test: QRService.validate_qr_code() zwraca bool.
    """
    with app.app_context():
        # Utwórz pracownika z QR
        emp = Employee(first_name="Test", last_name="User", email="test@example.com")
        db.session.add(emp)
        db.session.flush()

        qr_data, qr_exp = QRService.generate_credential()
        qr = QRCredential(employee_id=emp.id, qr_code_data=qr_data, expires_at=qr_exp, is_active=True)
        db.session.add(qr)
        db.session.commit()

        # Sprawdź: ważny QR
        assert QRService.validate_qr_code(qr_data) == True

        # Sprawdź: nieistniejący QR
        assert QRService.validate_qr_code("fake-qr") == False

        # Sprawdź: nieaktywny QR
        qr.is_active = False
        db.session.commit()
        assert QRService.validate_qr_code(qr_data) == False


def test_refresh_and_delete_qr_codes(app, client):
    """
    Test: refresh_expired_qr_codes() i delete_inactive_qr_codes().
    """
    with app.app_context():
        e1 = Employee(first_name="A", last_name="A", email="a@example.com")
        e2 = Employee(first_name="B", last_name="B", email="b@example.com")
        db.session.add_all([e1, e2])
        db.session.commit()

        # e1: wygasły (aktywny)
        old_code_e1 = QRCredential(
            employee_id=e1.id,
            qr_code_data="old-e1",
            expires_at=datetime.utcnow() - timedelta(days=2),
            is_active=True
        )
        # e2: nieaktywny
        old_code_e2 = QRCredential(
            employee_id=e2.id,
            qr_code_data="old-e2",
            expires_at=datetime.utcnow() + timedelta(days=5),
            is_active=False
        )
        db.session.add_all([old_code_e1, old_code_e2])
        db.session.commit()

        # 1. Odśwież wygasłe
        refreshed = refresh_expired_qr_codes()
        assert isinstance(refreshed, list)
        assert len(refreshed) == 1  # Tylko e1 (wygasły)
        assert refreshed[0]["employee_id"] == e1.id

        # Sprawdzenie: e1 ma nowy aktywny QR
        qr_e1_list = QRCredential.query.filter_by(employee_id=e1.id, is_active=True).all()
        assert len(qr_e1_list) == 1
        assert qr_e1_list[0].qr_code_data != "old-e1"

        # 2. Usuń nieaktywne
        deleted = delete_inactive_qr_codes()
        assert isinstance(deleted, dict)
        assert deleted["deleted_count"] >= 1

        # Brak nieaktywnych
        still_inactive = QRCredential.query.filter_by(is_active=False).all()
        assert len(still_inactive) == 0