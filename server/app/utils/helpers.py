from sqlalchemy import func
from sqlalchemy.orm import aliased
from datetime import datetime
from app.utils.db import db
from app.models.employee import Employee
from app.models.qr_code import QRCredential
from app.services.qr_service import QRService

def get_next_available_id():
    min_id = db.session.query(func.min(Employee.id)).scalar()

    # jeśli pusta
    if min_id is None or min_id >1:
        return 1
    
    # dziura-> alisay

    e1 = db.aliased(Employee)
    e2 = db.aliased(Employee)
    gap_id = db.session.query(func.min(e1.id + 1)).\
        outerjoin(e2, e2.id == e1.id + 1).\
        filter(e2.id == None).\
        scalar()
    
    if gap_id:
        return gap_id
    else: # max id
        max_id = db.session.query(func.max(Employee.id)).scalar()
        return max_id + 1
def delete_inactive_qr_codes():
    """
    Usuwa rekordy QRCredential, gdzie is_active == False.
    Szybsze, ale niszczy historię.
    """
    try:
        # szybkie masowe usunięcie
        deleted = db.session.query(QRCredential).filter_by(is_active=False).delete(synchronize_session=False)
        db.session.commit()
        return {"deleted_count": deleted}
    except Exception:
        db.session.rollback()
        raise

def refresh_expired_qr_codes(valid_hours: int = 24):
    """
    Oznacza wygasłe/nieaktywne wpisy jako nieaktywne i tworzy nowe QR dla powiązanych pracowników.
    Zwraca listę wygenerowanych pozycji: [{"employee_id","new_qr","expires_at"}, ...]
    """
    now = datetime.utcnow()
    results = []
    try:
        # znajdź employee_id które mają wygasłe (aktywny i expires_at < teraz) lub już nieaktywne wpisy
        expired = QRCredential.query.filter(
            QRCredential.expires_at != None,
            QRCredential.expires_at < now,
            QRCredential.is_active == True
        ).all()
        inactive = QRCredential.query.filter_by(is_active=False).all()

        employee_ids = {q.employee_id for q in (expired + inactive) if q.employee_id is not None}

        for emp_id in employee_ids:
            # oznacz wszystkie aktywne wpisy tego pracownika jako nieaktywne (archiwizacja)
            old_qs = QRCredential.query.filter_by(employee_id=emp_id, is_active=True).all()
            for o in old_qs:
                o.is_active = False
                db.session.add(o)

            # utwórz nowy QR
            new_code, new_exp = QRService.generate_credential(valid_hours)
            new_qr = QRCredential(employee_id=emp_id, qr_code_data=new_code, expires_at=new_exp, is_active=True)
            db.session.add(new_qr)
            results.append({"employee_id": emp_id, "new_qr": new_code, "expires_at": new_exp.isoformat()})

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return results