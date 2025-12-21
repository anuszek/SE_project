import os
import base64
import pytest
from app.models.employee import Employee
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
        db.session.query(Employee).delete()
        db.session.commit()

# --- TESTY ---

def test_register_employee_success(client, clean_db):
    """Testuje poprawną rejestrację pracownika z twarzą"""
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
    assert "employee_id" in data
    assert "qr_code" in data
    assert data['message'] == "Employee registered successfully"

def test_register_employee_duplicate_email(client, clean_db):
    """Testuje blokadę rejestracji na ten sam e-mail"""
    img_b64 = get_img_b64("faces_test/face.jpg")
    payload = {
        "first_name": "Ewa", "last_name": "Nowak",
        "email": "ewa@test.pl", "image": img_b64
    }
    # Pierwsza rejestracja
    client.post('/api/employees/register', json=payload)
    # Druga rejestracja (ten sam email)
    res = client.post('/api/employees/register', json=payload)
    
    assert res.status_code == 409
    assert res.get_json()['error'] == "Email already exists"

def test_get_all_employees(client, clean_db):
    """Testuje pobieranie listy wszystkich pracowników"""
    # Rejestrujemy kogoś
    img_b64 = get_img_b64("faces_test/face.jpg")
    client.post('/api/employees/register', json={
        "first_name": "Adam", "last_name": "Z", "email": "a@z.pl", "image": img_b64
    })
    
    res = client.get('/api/employees/all')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]['first_name'] == "Adam"

def test_modify_employee(client, clean_db):
    """Testuje zmianę danych osobowych pracownika"""
    # 1. Rejestracja
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Jan", "last_name": "K", "email": "jan@k.pl", "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']

    # 2. Modyfikacja
    mod_payload = {
        "employee_id": emp_id,
        "first_name": "Janusz",
        "last_name": "Kowalski",
        "email": "janusz@kowalski.pl"
    }
    res = client.put('/api/employees/modify_employee', json=mod_payload)
    assert res.status_code == 200
    
    # 3. Sprawdzenie w bazie
    with client.application.app_context():
        emp = Employee.query.get(emp_id)
        assert emp.first_name == "Janusz"
        assert emp.email == "janusz@kowalski.pl"

def test_deactivate_and_refresh_qr(client, clean_db):
    """Testuje cykl: dezaktywacja kodu QR -> generowanie nowego kodu"""
    # 1. Rejestracja
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Karol", "last_name": "W", "email": "k@w.pl", "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']
    old_qr = reg_res.get_json()['qr_code']

    # 2. Dezaktywacja
    res_inact = client.post('/api/employees/inactive_qr_code', json={"employee_id": emp_id})
    assert res_inact.status_code == 200
    
    with client.application.app_context():
        emp = Employee.query.get(emp_id)
        assert emp.qr_code.is_active is False

    # 3. Generowanie nowego QR
    res_new = client.post(f'/api/employees/{emp_id}/generate_new_qr_code')
    assert res_new.status_code == 200
    new_qr = res_new.get_json()['qr_code']
    assert new_qr != old_qr
    
    with client.application.app_context():
        assert Employee.query.get(emp_id).qr_code.is_active is True

def test_delete_employee(client, clean_db):
    """Testuje usuwanie pracownika"""
    # 1. Rejestracja
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Usuwalny", "last_name": "P", "email": "u@p.pl", "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']

    # 2. Usunięcie
    res_del = client.delete(f'/api/employees/{emp_id}/delete')
    assert res_del.status_code == 200
    
    # 3. Sprawdzenie czy zniknął
    res_get = client.get('/api/employees/all')
    assert len(res_get.get_json()) == 0

def test_modify_non_existent_employee(client, clean_db):
    """Testuje modyfikację nieistniejącego pracownika (404)"""
    res = client.put('/api/employees/modify_employee', json={
        "employee_id": 999, "first_name": "A", "last_name": "B", "email": "a@b.com"
    })
    assert res.status_code == 404