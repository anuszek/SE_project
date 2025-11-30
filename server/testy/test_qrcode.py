import base64
from datetime import datetime, timedelta
from unittest.mock import patch

from app.models.qr_code import QRCredential
from app.models.employee import Employee
from app.utils.db import db
from app.utils.helpers import refresh_expired_qr_codes, delete_inactive_qr_codes


def _fake_b64_image():
    return "data:image/jpeg;base64," + base64.b64encode(b"fake-image").decode("ascii")


def test_register_creates_qr_and_get_png_datauri(client):
    img_b64 = _fake_b64_image()
    fake_encoding = object()
    fake_bytes = b"fake-encoding-bytes"

    with patch('app.services.face_service.FaceServices.handle_base64_image') as mock_handle, \
         patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as mock_enc_to_bytes:

        mock_handle.return_value = b"img-bytes"
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
        emp_id = data["employee_id"]

        get_resp = client.get(f"/api/employees/{emp_id}/qr")
        assert get_resp.status_code == 200, get_resp.get_json()
        j = get_resp.get_json()
        assert "qr_code" in j and "qr_image" in j
        assert j["qr_image"].startswith("data:image/png;base64,")

        b64 = j["qr_image"].split(",", 1)[1]
        png_bytes = base64.b64decode(b64)
        assert len(png_bytes) > 8


def test_refresh_and_delete_qr_codes(app, client):
    """
    Używa nowych funkcji:
    - refresh_expired_qr_codes() -> oznacza stare i tworzy nowe dla pracowników (dla expired + inactive)
    - delete_inactive_qr_codes() -> usuwa wpisy is_active==False
    """
    with app.app_context():
        # przygotuj pracowników
        e1 = Employee(first_name="A", last_name="A", email="a@example.com")
        e2 = Employee(first_name="B", last_name="B", email="b@example.com")
        db.session.add_all([e1, e2])
        db.session.commit()

        # e1: wygasły, aktywny
        old_code_e1 = QRCredential(
            employee_id=e1.id,
            qr_code_data="old-e1",
            expires_at=datetime.utcnow() - timedelta(days=2),
            is_active=True
        )
        # e2: nieaktywny wpis
        old_code_e2 = QRCredential(
            employee_id=e2.id,
            qr_code_data="old-e2",
            expires_at=datetime.utcnow() + timedelta(days=5),
            is_active=False
        )
        db.session.add_all([old_code_e1, old_code_e2])
        db.session.commit()

        # odśwież (powinien utworzyć nowe aktywne kody dla e1 i e2 i oznaczyć stare jako nieaktywne)
        refreshed = refresh_expired_qr_codes()
        assert isinstance(refreshed, list)

        # sprawdź, że każdy pracownik ma teraz aktywny QR inny niż stary
        qr_e1_list = QRCredential.query.filter_by(employee_id=e1.id).all()
        assert any(q.is_active for q in qr_e1_list)
        active_qr_e1 = [q for q in qr_e1_list if q.is_active][0]
        assert active_qr_e1.qr_code_data != "old-e1"
        assert active_qr_e1.expires_at is not None and active_qr_e1.expires_at > datetime.utcnow()

        qr_e2_list = QRCredential.query.filter_by(employee_id=e2.id).all()
        assert any(q.is_active for q in qr_e2_list)
        active_qr_e2 = [q for q in qr_e2_list if q.is_active][0]
        assert active_qr_e2.qr_code_data != "old-e2"

        # teraz usuń wpisy nieaktywne
        deleted = delete_inactive_qr_codes()
        assert isinstance(deleted, dict)
        # upewnij się, że nie ma już nieaktywnych wpisów
        still_inactive = QRCredential.query.filter_by(is_active=False).all()
        assert len(still_inactive) == 0