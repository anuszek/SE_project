import pytest
from unittest.mock import patch
import numpy as np

def test_full_auth_flow_success(client):
    """
    Testuje pełny proces: 
    1. Rejestracja -> 2. Weryfikacja QR -> 3. Weryfikacja Twarzy
    """
    # --- 1. REJESTRACJA ---
    fake_encoding = np.zeros(128, dtype=np.float64)
    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as m_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as m_bytes:
        
        m_enc.return_value = fake_encoding
        m_bytes.return_value = b"fake-encoding-bytes"
        
        reg_payload = {
            'first_name': 'Auth', 'last_name': 'User', 
            'email': 'auth_success@test.com', 'image': 'data:image/jpeg;base64,AAA='
        }
        reg_res = client.post('/api/employees/register', json=reg_payload)
        assert reg_res.status_code == 201
        qr_code = reg_res.get_json()['qr_code']

    # --- 2. WERYFIKACJA QR ---
    with patch('app.services.qr_service.QRService.validate_qr_code') as m_qr_val:
        m_qr_val.return_value = True
        
        qr_res = client.post('/api/auth/qr', json={'qr_code': qr_code})
        assert qr_res.status_code == 200
        emp_id = qr_res.get_json()['employee_id']

    # --- 3. WERYFIKACJA TWARZY ---
    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as m_get, \
         patch('app.services.face_service.FaceServices.compare_faces') as m_comp:
        
        m_get.return_value = fake_encoding
        m_comp.return_value = True # Twarze pasują
        
        face_payload = {
            'employee_id': emp_id,
            'image': 'data:image/jpeg;base64,AAA='
        }
        final_res = client.post('/api/auth/face', json=face_payload)
        
        assert final_res.status_code == 200
        assert final_res.get_json()['status'] == 'granted'

def test_verify_qr_invalid(client):
    """Testuje odrzucenie błędnego kodu QR."""
    response = client.post('/api/auth/qr', json={'qr_code': 'invalid_code_xyz'})
    assert response.status_code == 401
    assert "denied" in response.get_json()['status']

def test_verify_face_mismatch(client):
    """
    Testuje sytuację, gdy pracownik istnieje, ale biometria nie pasuje.
    Używamy rejestracji wewnątrz testu, aby mieć poprawne ID.
    """
    # 1. NAJPIERW REJESTRUJEMY PRACOWNIKA (żeby uniknąć błędu 404)
    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as m_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as m_bytes:
        
        m_enc.return_value = np.zeros(128)
        m_bytes.return_value = b"original-face-encoding"
        
        reg_resp = client.post('/api/employees/register', json={
            'first_name': 'Jan', 'last_name': 'Testowy',
            'email': 'mismatch.test@example.com', 'image': 'data:image/jpeg;base64,AAA='
        })
        assert reg_resp.status_code == 201
        emp_id = reg_resp.get_json()['employee_id'] # Pobieramy RZECZYWISTE ID

    # 2. PRÓBUJEMY WERYFIKACJI DLA TEGO ID, ALE SYMULUJEMY BRAK DOPASOWANIA TWARZY
    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as m_get, \
         patch('app.services.face_service.FaceServices.compare_faces') as m_comp:
        
        m_get.return_value = np.ones(128) # Inny wektor twarzy
        m_comp.return_value = False      # SYMULACJA: Twarz nie pasuje!
        
        payload = {
            'employee_id': emp_id, # Używamy ID z kroku 1
            'image': 'data:image/jpeg;base64,AAA='
        }
        response = client.post('/api/auth/face', json=payload)

    # 3. SPRAWDZAMY CZY DOSTALIŚMY 401 (a nie 404)
    assert response.status_code == 401
    assert response.get_json()['status'] == 'denied'
    assert "nie pasuje" in response.get_json()['message']

def test_verify_qr_endpoint_logic(client, app):
    """Testuje integrację endpointu QR bezpośrednio z bazą danych."""
    with app.app_context():
        from app.models.employee import Employee
        from app.models.qr_code import QRCredential
        from app.utils.db import db
        from app.services.qr_service import QRService

        emp = Employee(first_name="Auth", last_name="Test", email="logic@test.pl")
        db.session.add(emp)
        db.session.flush()

        qr_data, qr_exp = QRService.generate_credential()
        qr = QRCredential(employee_id=emp.id, qr_code_data=qr_data, expires_at=qr_exp, is_active=True)
        db.session.add(qr)
        db.session.commit()

        resp = client.post("/api/auth/qr", json={"qr_code": qr_data})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "valid"

        qr.is_active = False
        db.session.commit()
        resp_inactive = client.post("/api/auth/qr", json={"qr_code": qr_data})
        assert resp_inactive.status_code == 401
