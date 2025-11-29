# tests/test_routes.py
from io import BytesIO
import pytest
from unittest.mock import patch
import numpy as np

def test_register_employee_success(client):
    """Testuje pełną ścieżkę rejestracji (mockując rozpoznawanie twarzy)."""
    
    # Przygotujmy dane
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@user.com"
    }
    
    # Tworzymy sztuczny plik zdjęcia (pusty strumień bajtów)
    from io import BytesIO
    fake_image = (BytesIO(b"fake_image_data"), 'face.jpg')

    # --- MAGIA MOCKOWANIA ---
    # Podmieniamy metodę get_encoding_from_image, żeby nie uruchamiała face_recognition
    # Zwracamy losowy wektor 128 liczb (taki jak zwraca biblioteka)
    fake_encoding = np.zeros(128, dtype=np.float64)

    with patch('app.services.face_service.FaceService.get_encoding_from_image') as mock_method:
        mock_method.return_value = fake_encoding
        
        # Wysyłamy żądanie POST
        response = client.post('/api/employees/register', data={
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@test.pl',
            'image': fake_image
        }, content_type='multipart/form-data')

    # Sprawdzamy czy sukces
    assert response.status_code == 201
    json_data = response.get_json()
    assert "Pracownik dodany" in json_data["message"]
    # ID powinno być 1, bo to pierwszy user w bazie testowej
    assert json_data["id"] == 1


def test_verify_failure_no_face(client):
    """Testuje sytuację, gdy na zdjęciu nie ma twarzy."""
    
    fake_image = (BytesIO(b"fake"), 'face.jpg')

    # Mockujemy tak, żeby zwrócił None (brak twarzy)
    with patch('app.services.face_service.FaceService.get_encoding_from_image') as mock_method:
        mock_method.return_value = None
        
        response = client.post('/api/employees/register', data={
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@test.pl',
            'image': fake_image
        }, content_type='multipart/form-data')

    assert response.status_code == 400
    assert "Nie wykryto twarzy" in response.get_json()["error"]