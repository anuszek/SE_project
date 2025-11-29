from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.utils.db import db
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.services.face_service import FaceService

# Tworzymy "Blueprint" - czyli moduł aplikacji
employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/register', method=['POST'])
def register_emplyee():

@employees_bp.route('/verify', method=['POST'])
def verify_emplyee(emplyee_face,emplyee_qe):
    # validate qr TO-DO
    # validacka qr zwraca id pracownika
    # przeszukiwanie bazy danych
    employee_id =1 #placeholder
    face_form_db = FaceCredential.query.filter(Employee.query.filter(employee_id))
    if FaceService.compera_faces(emplyee_face,face_form_db):
        return {
            'message': "Sukces"
        },200
    else:
        return {
            'message': "Bad face"
    },400