import pytest
from unittest.mock import patch
import numpy as np
import base64

def test_register_employee_success(client):
    """Testuje poprawną rejestrację pracownika."""
    # Symulacja obrazka
    full_base64_string = "data:image/jpeg;base64,VEVTVA=="
    fake_encoding = np.zeros(128, dtype=np.float64)

    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as mock_to_bytes, \
         patch('app.services.qr_service.QRService.generate_credential') as mock_qr:
        
        mock_get_enc.return_value = fake_encoding
        mock_to_bytes.return_value = b"fake-bytes"
        mock_qr.return_value = ("QR_MOCK_123", None) # kod, data_wygasniecia

        payload = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@test.com',
            'image': full_base64_string
        }
        
        response = client.post('/api/employees/register', json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert "Employee registered successfully" in data["message"]
    assert "qr_code" in data
    assert data["qr_code"] == "QR_MOCK_123"

def test_get_all_employees(client):
    """Testuje pobieranie listy pracowników."""
    response = client.get('/api/employees/all')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_employee_qr(client):
    """Testuje pobieranie kodu QR dla konkretnego pracownika (wymaga ID z bazy)."""
    # Uwaga: w testach integracyjnych najlepiej najpierw zarejestrować usera
    # Tutaj testujemy endpoint, zakładając że employee_id=1 istnieje lub dostaniemy 404
    response = client.get('/api/employees/1/qr')
    assert response.status_code in [200, 404]

# test_employees.py

def test_register_and_get_qr_flow(client):
    """Testuje, czy po rejestracji można pobrać kod QR dedykowanym endpointem."""
    img_b64 = "data:image/jpeg;base64,VEVTVA=="
    
    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as m_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as m_bytes:

        m_enc.return_value = np.zeros(128)
        m_bytes.return_value = b"bytes"

        # 1. Rejestracja
        resp = client.post("/api/employees/register", json={
            "first_name": "Jan", "last_name": "Kowalski",
            "email": "jan@test.pl", "image": img_b64
        })
        assert resp.status_code == 201
        emp_id = resp.get_json()["employee_id"]
        qr_from_reg = resp.get_json()["qr_code"]

        # 2. Pobranie QR przez GET /api/employees/<id>/qr
        get_resp = client.get(f"/api/employees/{emp_id}/qr")
        assert get_resp.status_code == 200
        assert get_resp.get_json()["qr_code"] == qr_from_reg