import os
import base64
import pytest
from app.models.employee import Employee
from app.models.qr_code import QRCredential
from app.utils.db import db

# --- HELPERS ---

def get_img_b64(path):
    """Pomocnik do generowania base64 dla testów"""
    if not os.path.exists(path):
        # Jeśli nie masz drugiego zdjęcia, test 'no_match' zostanie pominięty
        return None
    with open(path, "rb") as f:
        return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

@pytest.fixture
def registered_user(client):
    """Fixture, który rejestruje pracownika i zwraca jego dane do testów auth"""
    email = "auth_test@example.com"
    # Czyścimy bazę na wypadek śmieci
    old_emp = Employee.query.filter_by(email=email).first()
    if old_emp:
        db.session.delete(old_emp)
        db.session.commit()

    img_path = os.path.join("faces_test", "face.jpg")
    img_b64 = get_img_b64(img_path)
    
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "image": img_b64
    }
    res = client.post('/api/employees/register', json=payload)
    return res.get_json()  # Zawiera employee_id i qr_code

# --- TESTY QR (/qr) ---

def test_verify_qr_success(client, registered_user):
    """Sukces: Prawidłowy kod QR"""
    payload = {"qr_code": registered_user['qr_code']}
    res = client.post('/api/auth/qr', json=payload)
    
    assert res.status_code == 200
    assert res.get_json()['status'] == "valid"
    assert res.get_json()['employee_id'] == registered_user['employee_id']

def test_verify_qr_invalid(client):
    """Błąd: Kod QR nie istnieje w bazie"""
    res = client.post('/api/auth/qr', json={"qr_code": "invalid_qr_123"})
    assert res.status_code == 401
    assert "Nieprawidłowy" in res.get_json()['message']

def test_verify_qr_missing_field(client):
    """Błąd: Brak pola qr_code w JSON"""
    res = client.post('/api/auth/qr', json={})
    assert res.status_code == 400
    assert res.get_json()['error'] == "Brak kodu QR"

# --- TESTY FACE (/face) ---

def test_verify_face_success(client, registered_user):
    """Sukces: Twarz pasuje do zarejestrowanego wzorca"""
    img_b64 = get_img_b64(os.path.join("faces_test", "face.jpg"))
    payload = {
        "employee_id": registered_user['employee_id'],
        "image": img_b64
    }
    res = client.post('/api/auth/face', json=payload)
    
    assert res.status_code == 200
    assert res.get_json()['status'] == "granted"
    assert "Witaj" in res.get_json()['message']

def test_verify_face_no_match(client, registered_user):
    """Błąd: Twarz rozpoznana, ale to inna osoba (wymaga faces_test/other.jpg)"""
    other_img = os.path.join("faces_test", "other.jpg")
    if not os.path.exists(other_img):
        pytest.skip("Brak pliku other.jpg do testu błędnego dopasowania")
        
    img_b64 = get_img_b64(other_img)
    payload = {
        "employee_id": registered_user['employee_id'],
        "image": img_b64
    }
    res = client.post('/api/auth/face', json=payload)
    
    assert res.status_code == 401
    assert res.get_json()['status'] == "denied"
    assert "nie pasuje" in res.get_json()['message']

def test_verify_face_no_face_in_image(client, registered_user):
    """Błąd: Przesłano zdjęcie, na którym nie ma żadnej twarzy (np. czarny kwadrat)"""
    # Mały czarny kwadrat 1x1 w base64
    black_dot = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    payload = {
        "employee_id": registered_user['employee_id'],
        "image": black_dot
    }
    res = client.post('/api/auth/face', json=payload)
    
    assert res.status_code == 400
    assert "Nie wykryto twarzy" in res.get_json()['message']

def test_verify_face_wrong_employee_id(client):
    """Błąd: Próba weryfikacji twarzy dla nieistniejącego ID pracownika"""
    img_b64 = get_img_b64(os.path.join("faces_test", "face.jpg"))
    payload = {
        "employee_id": 999999,
        "image": img_b64
    }
    res = client.post('/api/auth/face', json=payload)
    
    assert res.status_code == 404
    assert "Brak wzorca" in res.get_json()['error']

def test_verify_face_missing_params(client):
    """Błąd: Brak wymaganych pól w żądaniu face"""
    res = client.post('/api/auth/face', json={"employee_id": 1})
    assert res.status_code == 400
    assert "Brak zdjęcia" in res.get_json()['error']

def test_verify_face_invalid_base64(client, registered_user):
    """Błąd: Przesłano uszkodzony string base64"""
    payload = {
        "employee_id": registered_user['employee_id'],
        "image": "data:image/jpeg;base64,not-a-real-base64-string!!!"
    }
    res = client.post('/api/auth/face', json=payload)
    
    # Zależnie od tego jak rzuca biblioteka, może być 500 (Exception) lub 400
    assert res.status_code in [400, 500]