import os
import base64
import pytest
from app.models.employee import Employee
from app.models.employee_face import FaceCredential  # <--- Dodany import
from app.models.qr_code import QRCredential
from app.utils.db import db

# --- HELPERS ---

def get_img_b64(path):
    """Konwertuje plik obrazu do Base64 na potrzeby testów"""
    if not os.path.exists(path):
        pytest.fail(f"Brak pliku testowego: {path}")
    with open(path, "rb") as f:
        return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

@pytest.fixture
def clean_db(client):
    """Czyści tabele pracowników przed każdym testem"""
    with client.application.app_context():
        db.session.query(QRCredential).delete()
        db.session.query(FaceCredential).delete() # <--- Czyścimy też twarze
        db.session.query(Employee).delete()
        db.session.commit()

# --- TESTY ---

def test_register_employee_success(client, clean_db):
    """Testuje poprawną rejestrację pracownika i ZAPIS ZDJĘCIA W BAZIE"""
    img_b64 = get_img_b64("faces_test/face.jpg")
    payload = {
        "first_name": "Michał",
        "last_name": "Tester",
        "email": "michal@test.pl",
        "image": img_b64
    }
    res = client.post('/api/employees/register', json=payload)
    
    assert res.status_code == 201
    data = res.get_json()
    emp_id = data['employee_id']

    # --- WERYFIKACJA BAZY DANYCH ---
    with client.application.app_context():
        # Sprawdzamy czy zdjęcie fizycznie trafiło do bazy (BLOB)
        face_cred = FaceCredential.query.filter_by(employee_id=emp_id).first()
        
        assert face_cred is not None
        assert face_cred.face_encoding is not None
        
        # TO JEST KLUCZOWE SPRAWDZENIE:
        assert face_cred.face_image is not None
        assert isinstance(face_cred.face_image, bytes) # Musi być bajtami
        assert len(face_cred.face_image) > 0 # Musi mieć jakąś zawartość

def test_register_employee_duplicate_email(client, clean_db):
    img_b64 = get_img_b64("faces_test/face.jpg")
    payload = {
        "first_name": "Ewa", "last_name": "Nowak",
        "email": "ewa@test.pl", "image": img_b64
    }
    client.post('/api/employees/register', json=payload)
    res = client.post('/api/employees/register', json=payload)
    
    assert res.status_code == 409
    assert res.get_json()['error'] == "Email already exists"

def test_get_all_employees(client, clean_db):
    img_b64 = get_img_b64("faces_test/face.jpg")
    client.post('/api/employees/register', json={
        "first_name": "Adam", "last_name": "Z", "email": "a@z.pl", "image": img_b64
    })
    
    res = client.get('/api/employees/all')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1

def test_modify_employee(client, clean_db):
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Jan", "last_name": "K", "email": "jan@k.pl", "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']

    mod_payload = {
        "first_name": "Janusz", "last_name": "Kowalski", "email": "janusz@kowalski.pl"
    }
    res = client.put(f'/api/employees/{emp_id}/modify_employee', json=mod_payload)
    
    assert res.status_code == 200
    
    with client.application.app_context():
        emp = db.session.get(Employee, emp_id)
        assert emp.first_name == "Janusz"

def test_deactivate_and_refresh_qr(client, clean_db):
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Karol", "last_name": "W", "email": "k@w.pl", "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']
    
    client.post(f'/api/employees/{emp_id}/switch_qr_state', json={"is_active": False})
    
    res_new_qr = client.post(f'/api/employees/{emp_id}/generate_new_qr_code')
    assert res_new_qr.status_code == 200
    
    with client.application.app_context():
        emp = db.session.get(Employee, emp_id)
        assert emp.qr_code.is_active is True

def test_delete_employee(client, clean_db):
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Usuwalny", "last_name": "P", "email": "u@p.pl", "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']

    res_del = client.delete(f'/api/employees/{emp_id}/delete')
    assert res_del.status_code == 200

def test_modify_non_existent_employee(client, clean_db):
    res = client.put('/api/employees/999/modify_employee', json={
         "first_name": "A", "last_name": "B", "email": "a@b.com"
    })
    assert res.status_code == 404