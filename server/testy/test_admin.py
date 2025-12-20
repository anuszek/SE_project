import pytest
from datetime import datetime, timedelta
from app.models.employee import Employee
from app.models.access_log import AccessLog
from app.utils.db import db

@pytest.fixture
def setup_admin_data(client):
    """Fixture przygotowujący dane do testów administracyjnych"""
    # Czyszczenie bazy
    AccessLog.query.delete()
    Employee.query.delete()
    db.session.commit()

    # 1. Tworzymy pracownika
    emp = Employee(
        id=10, 
        first_name="Admin", 
        last_name="Tester", 
        email="admin.test@firma.pl"
    )
    db.session.add(emp)
    db.session.flush()

    # 2. Tworzymy logi:
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    # Log dzisiejszy - sukces
    l1 = AccessLog(
        employee_id=emp.id,
        status="granted",
        is_granted=True, # Zgodnie z Twoim kodem w raporcie
        verification_method="face",
        timestamp=now
    )
    
    # Log dzisiejszy - odmowa
    l2 = AccessLog(
        employee_id=emp.id,
        status="denied",
        is_granted=False,
        verification_method="qr",
        timestamp=now
    )

    # Log wczorajszy - sukces
    l3 = AccessLog(
        employee_id=emp.id,
        status="granted",
        is_granted=True,
        verification_method="face",
        timestamp=yesterday
    )

    db.session.add_all([l1, l2, l3])
    db.session.commit()
    return emp

# --- TESTY GET /logs ---

def test_get_access_logs_success(client, setup_admin_data):
    """Testuje pobieranie listy ostatnich logów"""
    res = client.get('/api/admin/logs?limit=2')
    assert res.status_code == 200
    data = res.get_json()
    
    assert data['success'] is True
    assert len(data['logs']) == 2
    assert data['logs'][0]['employee_name'] == "Admin Tester"

# --- TESTY GET /stats ---

def test_get_admin_stats(client, setup_admin_data):
    """Testuje statystyki dashboardu"""
    res = client.get('/api/admin/stats')
    assert res.status_code == 200
    data = res.get_json()
    
    assert data['total_employees'] == 1
    # Sprawdzamy logi z dzisiaj (l1 i l2)
    assert data['today_access'] == 2
    assert data['today_denied'] == 1

# --- TESTY POST /raport ---

def test_generate_raport_all(client, setup_admin_data):
    """Raport bez filtrów (powinien zwrócić wszystko)"""
    res = client.post('/api/admin/raport', json={})
    assert res.status_code == 200
    assert res.get_json()['count'] == 3

def test_generate_raport_date_filter(client, setup_admin_data):
    """Raport filtrowany po dacie (tylko dzisiejsze)"""
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    payload = {
        "date_from": today_str,
        "date_to": today_str
    }
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    # Powinny być tylko l1 i l2 (l3 jest wczorajszy)
    assert res.get_json()['count'] == 2

def test_generate_raport_type_denied(client, setup_admin_data):
    """Raport filtrowany po typie 'denied'"""
    payload = {"entry_type": "denied"}
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] == 1
    assert data['data'][0]['is_granted'] is False

def test_generate_raport_employee_filter(client, setup_admin_data):
    """Raport filtrowany po konkretnym pracowniku"""
    payload = {"employee_id": setup_admin_data.id}
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    assert res.get_json()['count'] == 3

def test_generate_raport_invalid_date(client, setup_admin_data):
    """Błąd: Nieprawidłowy format daty"""
    payload = {"date_from": "12-12-2023"} # Zły format (powinien być RRRR-MM-DD)
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 400
    assert "Nieprawidłowy format daty" in res.get_json()['error']

def test_generate_raport_not_json(client):
    """Błąd: Żądanie nie jest JSONem"""
    res = client.post('/api/admin/raport', data="not a json")
    assert res.status_code == 400
    assert "Wymagany format JSON" in res.get_json()['error']