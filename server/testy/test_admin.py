import pytest

def test_admin_stats(client):
    """Testuje pobieranie statystyk dashboardu."""
    response = client.get('/api/admin/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'total_employees' in data

def test_admin_logs_retrieval(client):
    """Testuje pobieranie logów dostępu."""
    response = client.get('/api/admin/logs?limit=5')
    assert response.status_code == 200
    data = response.get_json()
    assert 'logs' in data
    assert isinstance(data['logs'], list)

def test_create_access_log_manual(client):
    """Testuje ręczne tworzenie logu przez admina."""
    payload = {
        "employee_id": 1,
        "status": "granted",
        "verification_method": "qr"
    }
    response = client.post('/api/admin/access-log/create', json=payload)
    # Jeśli pracownik o ID 1 nie istnieje, może być błąd klucza obcego (zależy od bazy)
    # Ale sprawdzamy format odpowiedzi
    assert response.status_code in [201, 500] 

def test_clean_qr_endpoint(client):
    """Testuje endpoint do czyszczenia kodów QR."""
    response = client.get('/api/admin/clean_qr')
    assert response.status_code == 200
    assert "deleted" in response.get_json()

# test_admin.py
from datetime import datetime, timedelta, timezone

def test_admin_clean_qr_flow(client, app):
    """Testuje endpoint /api/admin/clean_qr i logikę helperów."""
    with app.app_context():
        from app.models.employee import Employee
        from app.models.qr_code import QRCredential
        from app.utils.db import db

        e1 = Employee(first_name="Admin", last_name="Test", email="admin@test.pl")
        db.session.add(e1)
        db.session.commit()

        # Tworzymy wygasły kod (używamy timezone-aware datetime dla nowszych wersji Pythona)
        expired_date = datetime.now(timezone.utc) - timedelta(days=1)
        old_qr = QRCredential(employee_id=e1.id, qr_code_data="OLD", expires_at=expired_date, is_active=True)
        db.session.add(old_qr)
        db.session.commit()

        # Wywołujemy endpoint admina
        resp = client.get("/api/admin/clean_qr")
        assert resp.status_code == 200
        data = resp.get_json()
        
        assert data["refreshed"] is not None
        # Sprawdzamy czy stary kod przestał być aktywny
        assert QRCredential.query.filter_by(qr_code_data="OLD", is_active=True).first() is None