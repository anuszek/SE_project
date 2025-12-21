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
    """Testuje zmianę danych osobowych pracownika przez URL ID"""
    # 1. Rejestracja pracownika, aby otrzymać ID
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Jan", 
        "last_name": "K", 
        "email": "jan@k.pl", 
        "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']

    # 2. Przygotowanie danych do modyfikacji (bez ID w środku)
    mod_payload = {
        "first_name": "Janusz",
        "last_name": "Kowalski",
        "email": "janusz@kowalski.pl"
    }

    # 3. Wywołanie endpointu (ID przekazujemy w adresie URL)
    res = client.put(f'/api/employees/{emp_id}/modify_employee', json=mod_payload)
    
    # 4. Asercje
    assert res.status_code == 200
    assert res.get_json()['message'] == "Employee modified successfully"
    
    # 5. Sprawdzenie czy dane faktycznie zmieniły się w bazie
    with client.application.app_context():
        # Używamy nowoczesnego db.session.get zamiast .query.get, żeby uniknąć warningów
        emp = db.session.get(Employee, emp_id)
        assert emp.first_name == "Janusz"
        assert emp.last_name == "Kowalski"
        assert emp.email == "janusz@kowalski.pl"
def test_deactivate_and_refresh_qr(client, clean_db):
    """Testuje cykl: przełączanie stanu QR (switch) -> generowanie całkowicie nowego kodu"""
    
    # 1. REJESTRACJA
    img_b64 = get_img_b64("faces_test/face.jpg")
    reg_res = client.post('/api/employees/register', json={
        "first_name": "Karol", 
        "last_name": "W", 
        "email": "k@w.pl", 
        "image": img_b64
    })
    emp_id = reg_res.get_json()['employee_id']
    old_qr_data = reg_res.get_json()['qr_code']

    # 2. DEZAKTYWACJA (używając switch_qr_state)
    # URL zawiera ID, body zawiera flagę is_active
    res_switch_off = client.post(
        f'/api/employees/{emp_id}/switch_qr_state', 
        json={"is_active": False}
    )
    assert res_switch_off.status_code == 200
    assert res_switch_off.get_json()['is_active'] is False
    
    with client.application.app_context():
        emp = db.session.get(Employee, emp_id)
        assert emp.qr_code.is_active is False

    # 3. GENEROWANIE NOWEGO KODU QR
    # Ten endpoint zgodnie z Twoim kodem ustawia is_active na True automatycznie
    res_new_qr = client.post(f'/api/employees/{emp_id}/generate_new_qr_code')
    assert res_new_qr.status_code == 200
    
    data_new = res_new_qr.get_json()
    assert data_new['qr_code'] != old_qr_data  # Kod musi być inny
    
    with client.application.app_context():
        emp_updated = db.session.get(Employee, emp_id)
        assert emp_updated.qr_code.qr_code_data == data_new['qr_code']
        assert emp_updated.qr_code.is_active is True

    # 4. PONOWNA AKTYWACJA RĘCZNA (opcjonalnie - sprawdzenie switcha w drugą stronę)
    res_switch_on = client.post(
        f'/api/employees/{emp_id}/switch_qr_state', 
        json={"is_active": True}
    )
    assert res_switch_on.status_code == 200
    assert res_switch_on.get_json()['is_active'] is True
    
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