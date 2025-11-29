from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.utils.db import db
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.services.face_service import FaceServices
from app.utils.helpers import get_next_available_id

import re
import datetime

MIN_NAME_LEN =3
MAX_EMAIL_LEN = 300
# Tworzymy "Blueprint" - czyli moduł aplikacji
employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/register', methods=['POST'])
def register_emplyee():
    if not request.is_json:
        return jsonify({"error": "Zły format"}), 400
    data = request.get_json()
    first_name =  data.get('first_name')
    last_name = data.get('last_name')
    email= data.get('email')
    image = data.get('image')
    if not first_name or not last_name or not email or not image:
        return jsonify({
            'error':'Bad json sth missing'
        }), 400
    
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    first_name_pattern = r"^[A-Za-z0-9_.'-]+$"
    last_name_pattern = r"^[A-Za-z0-9_.'-]+$"
    if (
        not re.match(email_pattern, email)
        or not re.match(first_name, first_name_pattern)
        or not re.match(last_name, last_name_pattern)
        or not len(email) < MAX_EMAIL_LEN
        or not len(first_name) > MIN_NAME_LEN
        or not len(last_name) > MIN_NAME_LEN
    ):
        return jsonify({"message":"Invalid name, last name or email"}),400
    
    try:
        id = get_next_available_id()

        new_employee = Employee(
            id=id,   
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db.session.add(new_employee)
        db.session.flush() 

        new_face = FaceCredential(
            employee_id=new_employee.id, 
            face_encoding=image,
            face_image_path="memory"
        )
        db.session.add(new_face)
        db.session.flush()
        # to samo dla qr, gerneowanie i dodanie, 

       
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    #qr -> generowanie jak bedzie logika
    #image -> po face regontionion


@employees_bp.route('/verify', method=['POST'])
def verify_emplyee():
    if not request.is_json:
        return jsonify({"error": "Zły format"}), 400
    data = request.get_json()
    qr_input=data.get('qr_coode') # zmianic nazwy odpwowiednie
    image_input= data.get('image')

    if not qr_input or not image_input:
        return jsonify({'error':'Bad type brakuje image albo qr'}), 400
    
    # validate qr TO-DO
    
    employee_id =1 #placeholder
    # jeli image w zlym typie dto dopiac
    employee_face_from_db= FaceCredential.query.filter(employee_id=employee_id).first()
    is_match= FaceServices.compare_faces(employee_face_from_db,image_input)
    
    if is_match:
        employee = Employee.query.get(employee_id)
        return jsonify({
            "status": "granted",
            "message": f"Dostęp przyznany. Witaj, {employee.first_name}!",
            "employee_id": employee.id
        }), 200
    else:
        # KOD QR SIĘ ZGADZA, ALE TWARZ NIE
        return jsonify({
            "status": "denied",
            "message": "Weryfikacja biometryczna nieudana. Twarz nie pasuje do kodu QR."
        }), 401