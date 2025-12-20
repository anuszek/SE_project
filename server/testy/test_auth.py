import pytest
from datetime import datetime, timedelta
from app.models.employee import Employee
from app.models.access_log import AccessLog
from app.utils.db import db

@pytest.fixture
def setup_admin_data(client):
    """
    Fixture przygotowujący dane testowe dla panelu administratora.
    Czyści bazę i tworzy testowego pracownika oraz logi.
    """
    with client.application.app_context():
        # 1. Czyszczenie bazy danych przed każdym testem
        db.session.query(AccessLog).delete()
        db.session.query(Employee).delete()
        db.session.commit()

        # 2. Tworzenie testowego pracownika
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

        # 4. Tworzenie logów (używając pola 'status' zgodnie z modelem)
        # Log 1: Dzisiaj, przyznany (face)
        l1 = AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=now
        )
        # Log 2: Dzisiaj, odmowa (qr)
        l2 = AccessLog(
            employee_id=emp.id,
            status="denied",
            verification_method="qr",
            timestamp=now
        )
        # Log 3: Wczoraj, przyznany (face)
        l3 = AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=yesterday
        )

        db.session.add_all([l1, l2, l3])
        db.session.commit()
        
        return emp

# --- TESTY LOGÓW ---

def test_get_access_logs_success(client, setup_admin_data):
    """Testuje pobieranie ostatnich logów z limitem"""
    res = client.get('/api/admin/logs?limit=2')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['logs']) == 2
    assert data['logs'][0]['employee_name'] == "Admin Tester"

# --- TESTY STATYSTYK ---

def test_get_admin_stats(client, setup_admin_data):
    """Testuje statystyki dashboardu (liczenie dzisiejszych wejść)"""
    res = client.get('/api/admin/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_employees'] == 1
    assert data['today_access'] == 2  # l1 i l2 są z dzisiaj
    assert data['today_denied'] == 1  # tylko l2

# --- TESTY RAPORTÓW ---

def test_generate_raport_all(client, setup_admin_data):
    """Test generowania raportu bez żadnych filtrów"""
    res = client.post('/api/admin/raport', json={})
    assert res.status_code == 200
    assert res.get_json()['count'] == 3

def test_generate_raport_date_filter(client, setup_admin_data):
    """Test filtrowania raportu po dacie (tylko dzisiejsze zdarzenia)"""
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    payload = {
        "date_from": today_str,
        "date_to": today_str
    }
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    assert res.get_json()['count'] == 2 # l1 i l2

def test_generate_raport_type_denied(client, setup_admin_data):
    """Test filtrowania raportu po statusie 'denied'"""
    payload = {"entry_type": "denied"}
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] == 1
    assert data['data'][0]['status'] == "denied"

def test_generate_raport_employee_filter(client, setup_admin_data):
    """Test filtrowania raportu dla konkretnego pracownika"""
    payload = {"employee_id": setup_admin_data.id}
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    assert res.get_json()['count'] == 3

def test_generate_raport_invalid_date(client, setup_admin_data):
    """Test obsługi błędu przy nieprawidłowym formacie daty"""
    payload = {"date_from": "31-12-2023"} # Błędny format (powinien być RRRR-MM-DD)
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 400
    assert "Nieprawidłowy format daty" in res.get_json()['error']

def test_generate_raport_not_json(client):
    """Test obsługi błędu, gdy zapytanie nie jest JSONem"""
    res = client.post('/api/admin/raport', data="zwykły tekst")
    assert res.status_code == 400
    assert "Wymagany format JSON" in res.get_json()['error']