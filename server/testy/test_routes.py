import pytest
from unittest.mock import patch
import numpy as np
import base64
import json

def test_register_employee_json_base64(client):
    """
    Testuje rejestrację.
    """
    real_image_path = "../faces_test/face.jpg"
    
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
    assert "qr_code" in json_data

def test_verify_employee_success(client):
    """
    Testuje pełny proces: Rejestracja -> Weryfikacja.
    """
    real_image_path = "../faces_test/face.jpg"
    
    # 1. Przygotowanie zdjęcia (Base64)
    with open(real_image_path, "rb") as img_file:
        file_content = img_file.read()
        base64_string = base64.b64encode(file_content).decode('utf-8')
        full_base64_string = f"data:image/jpeg;base64,{base64_string}"

    # 2. Definiujemy "stały" wektor twarzy (np. same zera)
    # Dzięki temu przy rejestracji zapiszemy zera, a przy weryfikacji
    # system "zobaczy" zera i uzna, że to ta sama osoba.
    fake_encoding = np.zeros(128, dtype=np.float64)


    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_method:
        mock_method.return_value = fake_encoding
        
        # --- KROK A: REJESTRACJA (Żeby mieć kogo weryfikować) ---
        reg_payload = {
            'first_name': 'Weryfikowany',
            'last_name': 'Uzytkownik',
            'email': 'verify.me@test.com',
            'image': full_base64_string
        }
        reg_resp = client.post('/api/employees/register', json=reg_payload)
        assert reg_resp.status_code == 201
        qr_code = reg_resp.get_json()["qr_code"]

        # --- KROK B: WERYFIKACJA ---
        verify_payload = {
            'image': full_base64_string,
            'qr_code': qr_code
        }
        
        response = client.post('/api/employees/verify', json=verify_payload)

    # 3. Sprawdzenie wyników
    json_data = response.get_json()

    # Debugowanie w razie błędu
    if response.status_code != 200:
        print(f"BŁĄD WERYFIKACJI: {json_data}")

    assert response.status_code == 200
    assert json_data["status"] == "granted"
    assert "Dostęp przyznany" in json_data["message"]
    assert "employee_id" in json_data


def test_verify_employee_failure(client):
    """
    Testuje sytuację, gdy twarz nie pasuje (Symulacja innej osoby).
    """
    real_image_path = "../faces_test/face.jpg"
    with open(real_image_path, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode('utf-8')
        full_base64 = f"data:image/jpeg;base64,{base64_str}"

    # Wektor 1: Same zera (Dla osoby rejestrowanej)
    face_A = np.zeros(128, dtype=np.float64)
    
    # Wektor 2: Same jedynki (Dla osoby próbującej wejść)
    # face_recognition.compare_faces(zera, jedynki) zwróci False, bo są różne
    face_B = np.ones(128, dtype=np.float64)

    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
         patch('app.services.face_service.FaceServices.encoding_to_bytes') as mock_enc_to_bytes, \
         patch('app.services.face_service.FaceServices.compare_faces') as mock_compare:

        # 1. Rejestrujemy Osobę A (Mock zwraca zera)
        mock_get_enc.return_value = face_A
        mock_enc_to_bytes.return_value = b"enc-A"
        reg_resp = client.post('/api/employees/register', json={
            'first_name': 'Osoba', 'last_name': 'Testowa', 'email': 'osoba.testowa@example.com', 'image': full_base64
        })
        assert reg_resp.status_code == 201, reg_resp.get_json()
        qr_code = reg_resp.get_json()["qr_code"]

        # 2. Próbujemy wejść jako Osoba B (Mock zwraca jedynki)
        mock_get_enc.return_value = face_B
        mock_compare.return_value = False
        response = client.post('/api/employees/verify', json={'image': full_base64, 'qr_code': qr_code})

    # Oczekujemy odrzucenia
    assert response.status_code == 401
    assert response.get_json()["status"] == "denied"

def test_verify_missing_qr_code(client):
    """
    Testuje weryfikację bez QR -> error 400.
    """
    real_image_path = "../faces_test/face.jpg"
    with open(real_image_path, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode('utf-8')
        full_base64 = f"data:image/jpeg;base64,{base64_str}"

    fake_encoding = np.zeros(128, dtype=np.float64)

    with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc:
        mock_get_enc.return_value = fake_encoding
        
        response = client.post('/api/employees/verify', json={'image': full_base64})
        # Brak qr_code -> 400

    assert response.status_code == 400
    assert "qr_code" in response.get_json()["error"].lower()