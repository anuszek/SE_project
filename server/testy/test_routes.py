import pytest
from unittest.mock import patch
import numpy as np
import base64
import json

def test_register_employee_json_base64(client):
    """
    Testuje rejestrację BEZ QR (tylko zdjęcie i dane).
    """
    real_image_path = "/home/fisher/SE_project/faces_test/face.jpg"
    
    # Otwórz prawdziwy plik
    with open(real_image_path, "rb") as img_file:
        file_content = img_file.read()
        base64_string = base64.b64encode(file_content).decode('utf-8')
        full_base64_string = f"data:image/jpeg;base64,{base64_string}"

    # Mockujemy face_recognition (zwracamy wektor zer)
    fake_encoding = np.zeros(128, dtype=np.float64)

    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_method:
        mock_method.return_value = fake_encoding
        
        # Wysyłamy JSON bez QR
        payload = {
            'first_name': 'Test',
            'last_name': 'NoQR',
            'email': 'noqr@test.com',
            'image': full_base64_string
        }
        
        response = client.post('/api/employees/register', json=payload)

    # Diagnostyka błędu
    if response.status_code != 201:
        print(f"BŁĄD: {response.get_json()}")

    assert response.status_code == 201
    json_data = response.get_json()
    
    assert "Employee registered successfully" in json_data["message"]
    assert "employee_id" in json_data
    # Upewniamy się, że NIE MA tu qr_code (bo go wyłączyliśmy)
    assert "qr_code" not in json_data