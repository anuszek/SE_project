import pytest
from datetime import datetime, timedelta
from app.models.employee import Employee
from app.models.access_log import AccessLog
from app.utils.db import db

@pytest.fixture
def setup_admin_data(client):
    """
    Fixture przygotowujący dane testowe.
    Model AccessLog używa pola 'status' (string), a nie 'is_granted'.
    """
    with client.application.app_context():
        # 1. Czyszczenie bazy danych przed testem
        db.session.query(AccessLog).delete()
        db.session.query(Employee).delete()
        db.session.commit()

        # 2. Tworzenie pracownika
        emp = Employee(
            id=10, 
            first_name="Admin", 
            last_name="Tester", 
            email="admin.test@firma.pl"
        )
        db.session.add(emp)
        db.session.flush()

        # 3. Przygotowanie dat
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        # 4. Tworzenie logów - ZWRÓĆ UWAGĘ: status jest tylko RAZ i jest STRINGIEM
        # Log 1: Dzisiaj, sukces
        l1 = AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=now
        )
        
        # Log 2: Dzisiaj, odmowa
        l2 = AccessLog(
            employee_id=emp.id,
            status="denied",
            verification_method="qr",
            timestamp=now
        )

        # Log 3: Wczoraj, sukces
        l3 = AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=yesterday
        )

        db.session.add_all([l1, l2, l3])
        db.session.commit()
        return emp

# --- TESTY DLA /logs ---

def test_get_access_logs(client, setup_admin_data):
    """Testuje pobieranie ostatnich logów (GET /logs)"""
    res = client.get('/api/admin/logs?limit=10')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    # Weryfikacja czy poprawnie dołączono imię i nazwisko
    assert data['logs'][0]['employee_name'] == "Admin Tester"

# --- TESTY DLA /stats ---

def test_get_admin_stats(client, setup_admin_data):
    """Testuje statystyki dashboardu (GET /stats)"""
    res = client.get('/api/admin/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_employees'] == 1
    assert data['today_access'] == 2  # l1 i l2
    assert data['today_denied'] == 1  # l2 (denied)

# --- TESTY DLA /raport ---

def test_generate_raport_no_filters(client, setup_admin_data):
    """Testuje raport bez filtrów (POST /raport)"""
    res = client.post('/api/admin/raport', json={})
    assert res.status_code == 200
    assert res.get_json()['count'] == 3

def test_generate_raport_date_filter(client, setup_admin_data):
    """Testuje raport filtrowany po dacie (tylko dzisiejsze)"""
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    payload = {
        "date_from": today_str,
        "date_to": today_str
    }
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    assert res.get_json()['count'] == 2 # l1 i l2

def test_generate_raport_invalid_json(client):
    """Testuje obsługę błędu formatu JSON"""
    res = client.post('/api/admin/raport', data="nie-json")
    assert res.status_code == 400
    assert "Wymagany format JSON" in res.get_json()['error']

def test_generate_raport_bad_date(client, setup_admin_data):
    """Testuje obsługę błędnego formatu daty"""
    res = client.post('/api/admin/raport', json={"date_from": "2025/12/20"})
    assert res.status_code == 400
    assert "Nieprawidłowy format daty" in res.get_json()['error']