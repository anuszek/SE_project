from sqlalchemy import func
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta
from app.utils.db import db
from app.models.employee import Employee
from app.models.qr_code import QRCredential
from app.services.qr_service import QRService

def get_next_available_id():
    """
    Finds the next available Employee ID, filling gaps if any.
    """
    min_id = db.session.query(func.min(Employee.id)).scalar()

    if min_id is None or min_id >1:
        return 1

    e1 = db.aliased(Employee)
    e2 = db.aliased(Employee)
    gap_id = db.session.query(func.min(e1.id + 1)).\
        outerjoin(e2, e2.id == e1.id + 1).\
        filter(e2.id == None).\
        scalar()
    
    if gap_id:
        return gap_id
    else: 
        max_id = db.session.query(func.max(Employee.id)).scalar()
        return max_id + 1

def refresh_expired_qr_codes(valid_minutes: int = 3600):
    """
    Refreshes only expired QR entries for all employees.
    Overwrites the old code with a new one.
    """
    now = datetime.utcnow()
    results = []
    try:
        expired = QRCredential.query.filter(
            QRCredential.expires_at != None,
            QRCredential.expires_at < now,
            QRCredential.is_active == True
        ).all()

        for qr in expired:
            new_code, new_exp = QRService.generate_credential(valid_minutes)
            qr.qr_code_data = new_code
            qr.expires_at = new_exp
            db.session.add(qr)
            results.append({
                "employee_id": qr.employee_id, 
                "new_qr": new_code, 
                "expires_at": new_exp.isoformat()
            })

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return results

def clear_expired_logs(retention_months: int = 6):
    """
    Deletes access logs older than retention_months.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=retention_months*30)
    try:
        deleted = AccessLog.query.filter(AccessLog.timestamp < cutoff_date).delete()
        db.session.commit()
        return deleted
    except Exception:
        db.session.rollback()
        raise