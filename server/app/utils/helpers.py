from sqlalchemy import func
from app.utils.db import db
from app.models.employee import Employee

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