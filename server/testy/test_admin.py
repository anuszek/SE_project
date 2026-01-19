import pytest
from datetime import datetime, timedelta
from app.models.employee import Employee
from app.models.access_log import AccessLog
from app.utils.db import db

@pytest.fixture
def setup_admin_data(client):
    """
    Fixture preparing test data.
    The AccessLog model uses the 'status' field (string), not 'is_granted'.
    """
    with client.application.app_context():
        db.session.query(AccessLog).delete()
        db.session.query(Employee).delete()
        db.session.commit()

        emp = Employee(
            id=10, 
            first_name="Admin", 
            last_name="Tester", 
            email="admin.test@firma.pl"
        )
        db.session.add(emp)
        db.session.flush()

        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        l1 = AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=now
        )
        
        l2 = AccessLog(
            employee_id=emp.id,
            status="denied",
            verification_method="qr",
            timestamp=now
        )

        l3 = AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=yesterday
        )

        db.session.add_all([l1, l2, l3])
        db.session.commit()
        return emp

def test_get_access_logs(client, setup_admin_data):
    """
    Tests fetching recent logs (GET /logs)
    """
    res = client.get('/api/admin/logs?limit=10')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['logs'][0]['employee_name'] == "Admin Tester"

def test_get_admin_stats(client, setup_admin_data):
    """
    Tests dashboard statistics (GET /stats)
    """
    res = client.get('/api/admin/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_employees'] == 1
    assert data['today_access'] == 2
    assert data['today_denied'] == 1  

def test_generate_raport_no_filters(client, setup_admin_data):
    """
    Tests report generation without filters (POST /raport)
    """
    res = client.post('/api/admin/raport', json={})
    assert res.status_code == 200
    assert res.get_json()['count'] == 3

def test_generate_raport_date_filter(client, setup_admin_data):
    """
    Tests report filtered by date (only today's)
    """
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    payload = {
        "date_from": today_str,
        "date_to": today_str
    }
    res = client.post('/api/admin/raport', json=payload)
    assert res.status_code == 200
    assert res.get_json()['count'] == 2 

def test_generate_raport_invalid_json(client):
    """
    Tests handling of JSON format error
    """
    res = client.post('/api/admin/raport', data="nie-json")
    assert res.status_code == 400
    assert "JSON format required" in res.get_json()['error']

def test_generate_raport_bad_date(client, setup_admin_data):
    """
    Tests handling of invalid date format
    """
    res = client.post('/api/admin/raport', json={"date_from": "2025/12/20"})
    assert res.status_code == 400
    assert "Invalid date format" in res.get_json()['error']

def test_generate_raport_employee_stats(client):
    """
    Tests employee statistics in report when employee_id is specified
    """
    with client.application.app_context():
        db.session.query(AccessLog).delete()
        db.session.query(Employee).delete()
        db.session.commit()

        emp = Employee(
            id=20, 
            first_name="Stats", 
            last_name="Test", 
            email="stats.test@company.com"
        )
        db.session.add(emp)
        db.session.flush()

        now = datetime.utcnow()
        day1 = now - timedelta(days=2)
        day2 = now - timedelta(days=1)
        
        db.session.add(AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="qr",
            timestamp=day1
        ))
        db.session.add(AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=day1 + timedelta(hours=8)
        ))
        
        db.session.add(AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="qr",
            timestamp=day2
        ))
        db.session.add(AccessLog(
            employee_id=emp.id,
            status="denied",
            verification_method="face",  
            timestamp=day2 + timedelta(seconds=5)
        ))
        
        db.session.add(AccessLog(
            employee_id=emp.id,
            status="granted",
            verification_method="face",
            timestamp=now
        ))
        
        db.session.commit()

    res = client.post('/api/admin/raport', json={"employee_id": 20})
    assert res.status_code == 200
    
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['count'] == 5
    
    assert 'employee_stats' in data
    stats = data['employee_stats']
    
    assert stats['total_entries'] == 5
    assert stats['successful_entries'] == 4
    assert stats['unique_working_days'] == 3  
    assert stats['failed_face_verifications'] == 1
    assert stats['success_percentage'] == 80.0  
