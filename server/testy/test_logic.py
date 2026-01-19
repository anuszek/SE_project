from app.utils.db import db
from app.models.employee import Employee
from app.utils.helpers import get_next_available_id

def test_get_id_empty_db(app):
    """
    If DB is empty, the next ID should be 1.
    """
    with app.app_context():
        assert get_next_available_id() == 1

def test_get_id_sequence(app):
    """
    If we have 1, 2, 3 -> ID should be 4.
    """
    with app.app_context():
        db.session.add(Employee(id=1, first_name="Addd", last_name="Bddddddddddddd", email="a@add.com"))
        db.session.add(Employee(id=2, first_name="Cddd", last_name="Ddddddddddddd", email="c@cdd.com"))
        db.session.add(Employee(id=3, first_name="Edddd", last_name="Fdddd", email="e@edd.com"))
        db.session.commit()

        assert get_next_available_id() == 4

def test_get_id_gap(app):
    """
    If we have 1, 3 -> ID should be 2 (gap).
    """
    with app.app_context():
        db.session.add(Employee(id=1, first_name="Addddd", last_name="Bddd", email="addddddddddd@add.com"))
        db.session.add(Employee(id=3, first_name="Eddddd", last_name="Fdddd", email="eddddddddd@edd.com"))
        db.session.commit()

        assert get_next_available_id() == 2

def test_get_id_gap_at_start(app):
    """
    If we have 2, 3 -> ID should be 1.
    """
    with app.app_context():
        db.session.add(Employee(id=2, first_name="Cdddd", last_name="Dddddd", email="cqweqweqe@com.com"))
        db.session.add(Employee(id=3, first_name="Edddd", last_name="Fddddd", email="easdasdasda@e.com"))
        db.session.commit()

        assert get_next_available_id() == 1